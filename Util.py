
import sys, os
from PTTLibrary import PTT
from datetime import date, timedelta

PTTBot = None
Board = 'Wanted'
Moderators = ['gogin', 'LittleCalf']


def getToday():
    ErrCode, NewestIndex = PTTBot.getNewestIndex(Board=Board)

    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
        sys.exit()
    
    if NewestIndex == -1:
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
        sys.exit()

    for i in range(20):

        ErrCode, Post = PTTBot.getPost(Board, PostIndex=NewestIndex - i)

        if ErrCode == PTT.ErrorCode.PostDeleted:
            # if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
            #     # PTTBot.Log('文章被原 PO 刪掉了')
            #     pass
            # elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
            #     # PTTBot.Log('文章被版主刪掉了')
            #     pass
            # continue
            pass
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
            continue
        
        NewestIndex = NewestIndex - i

        break
    
    # print(Post.getDate())
    result = Post.getListDate()
    return NewestIndex, result

def getYesterDay(TodayOldestIndex):

    ResultIndex = 0

    for i in range(1, 20):
    
        ErrCode, Post = PTTBot.getPost(Board, PostIndex=TodayOldestIndex - i)

        if ErrCode == PTT.ErrorCode.PostDeleted:
            if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
                PTTBot.Log('文章被原 PO 刪掉了')
            elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
                PTTBot.Log('文章被版主刪掉了')
            # continue
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
            continue
        ResultIndex = TodayOldestIndex - i
        break
    result = Post.getListDate()
    return ResultIndex, result


def findFirstIndex(NewestIndex, Todaty, show=False):

    StartIndex = 1
    EndIndex = NewestIndex

    CurrentIndex = int((StartIndex + EndIndex) / 2)
    CurrentToday = ''
    LastCurrentToday = ''
    RetryIndex = 0

    while True:
        if show:
            PTTBot.Log('嘗試: ' + str(CurrentIndex))
        ErrCode, Post = PTTBot.getPost(Board, PostIndex=CurrentIndex)

        if ErrCode == PTT.ErrorCode.PostDeleted:

            pass
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
            CurrentIndex = StartIndex + RetryIndex
            RetryIndex += 1
            continue
        elif Post.getDate() is None:
            CurrentIndex = StartIndex + RetryIndex
            RetryIndex += 1
            continue
        
        RetryIndex = 0
        for i in range(1, 20):

            ErrCode, LastPost = PTTBot.getPost(Board, PostIndex=CurrentIndex - i)

            if ErrCode == PTT.ErrorCode.PostDeleted:
                pass
            elif ErrCode != PTT.ErrorCode.Success:
                if show:
                    PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
                continue
            elif LastPost is None:
                continue
            elif LastPost.getDate() is None:
                continue

            if show:
                PTTBot.Log('找到上一篇: ' + str(CurrentIndex - i))

            break
        CurrentToday = Post.getListDate()
        LastCurrentToday = LastPost.getListDate()

        if show:
            print('LastCurrentToday: ' + LastCurrentToday)
            print('CurrentToday: ' + CurrentToday)
            print(StartIndex)
            print(EndIndex)
        
        if CurrentToday == Todaty and LastCurrentToday != Todaty:
            return CurrentIndex
        if CurrentToday == Todaty and LastCurrentToday == Todaty:
            EndIndex = CurrentIndex - 1  
        elif CurrentToday != Todaty and LastCurrentToday != Todaty:
            StartIndex = CurrentIndex + 1
        CurrentIndex = int((StartIndex + EndIndex) / 2)


def getDate(TimeDel, PTTSytle=True):
    PassDay = date.today() - timedelta(TimeDel)

    PassDate = PassDay.strftime("%m/%d")
    # print('>' + PassDate + '<')
    if PTTSytle and PassDate.startswith('0'):
        PassDate = LastDate[1:]
    return PassDate



def findCurrentDateFirst(NewestIndex, DayAgo, show=False):
    
    global var1

    CurrentDate_0 = getDate(DayAgo + 1, PTTSytle=False).replace('/', '').strip()
    CurrentDate_1 = getDate(DayAgo, PTTSytle=False).replace('/', '').strip()
    FinishTarget = int(CurrentDate_0 + CurrentDate_1)

    StartIndex = 1
    EndIndex = NewestIndex

    CurrentIndex = int((StartIndex + EndIndex) / 2)
    CurrentToday = ''
    LastCurrentToday = ''
    RetryIndex = 0

    while True:
        if show:
            PTTBot.Log('嘗試: ' + str(CurrentIndex))
        ErrCode, Post_1 = PTTBot.getPost(Board, PostIndex=CurrentIndex)

        if ErrCode == PTT.ErrorCode.PostDeleted:
            pass
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
            CurrentIndex = StartIndex + RetryIndex
            RetryIndex += 1
            continue
        elif Post_1.getDate() is None:
            CurrentIndex = StartIndex + RetryIndex
            RetryIndex += 1
            continue
        
        RetryIndex = 0
        for i in range(1, 40):

            ErrCode, Post_0 = PTTBot.getPost(Board, 
                                             PostIndex=CurrentIndex - i)

            if ErrCode == PTT.ErrorCode.PostDeleted:
                pass
            elif ErrCode != PTT.ErrorCode.Success:
                if show:
                    PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
                continue
            elif Post_0 is None:
                continue
            elif Post_0.getDate() is None:
                continue

            if show:
                PTTBot.Log('找到上一篇: ' + str(CurrentIndex - i))

            break
        CurrentDate_0 = Post_0.getListDate().replace('/', '').strip()
        if len(CurrentDate_0) < 4:
            CurrentDate_0 = '0' + CurrentDate_0
        CurrentDate_1 = Post_1.getListDate().replace('/', '').strip()
        if len(CurrentDate_1) < 4:
            CurrentDate_1 = '0' + CurrentDate_1
        
        CurrentTarget = int(CurrentDate_0 + CurrentDate_1)

        if show:
            print('CurrentDate_0: ' + CurrentDate_0)
            print('CurrentDate_1: ' + CurrentDate_1)
            print('CurrentTarget: ' + str(CurrentTarget))
            print('FinishTarget: ' + str(FinishTarget))
            print(StartIndex)
            print(EndIndex)
        
        if CurrentTarget == FinishTarget:
            return CurrentIndex
        if CurrentTarget > FinishTarget:
            EndIndex = CurrentIndex - 1  
        elif CurrentTarget < FinishTarget:
            StartIndex = CurrentIndex + 1
        CurrentIndex = int((StartIndex + EndIndex) / 2)
        

def findPostRrange(DayAgo, show=False):
    ErrCode, NewestIndex = PTTBot.getNewestIndex(Board=Board)

    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
        sys.exit()
    
    if NewestIndex == -1:
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
        sys.exit()
    
    Start = findCurrentDateFirst(NewestIndex, DayAgo, show=False)
    End = findCurrentDateFirst(NewestIndex, DayAgo - 1, show=False) - 1

    if show:
        print('Result', Start, End)

    return Start, End

    # for i in range(10):
    #     PassDay = date.today() - timedelta(1 + i)

    #     PassDate = PassDay.strftime("%m/%d")
    #     if PassDate == Date:

    #         LastDate = (date.today() - timedelta(2 + i)).strftime("%m/%d")
    #         NextDate = (date.today() - timedelta(    i)).strftime("%m/%d")

    #         break
    