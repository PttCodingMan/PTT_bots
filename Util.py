
import sys, os
from PTTLibrary import PTT

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
    while True:
        if show:
            PTTBot.Log('嘗試: ' + str(CurrentIndex))
        ErrCode, Post = PTTBot.getPost(Board, PostIndex=CurrentIndex)

        if ErrCode == PTT.ErrorCode.PostDeleted:
            # if Post != None:
                # if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
                #     PTTBot.Log('文章被原 PO 刪掉了')
                # elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
                #     PTTBot.Log('文章被版主刪掉了')
            
            # CurrentIndex += 1
            # continue
            pass
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
            CurrentIndex += 1
            continue
        elif Post.getDate() == None:
            CurrentIndex += 1
            continue
        
        for i in range(1, 20):

            ErrCode, LastPost = PTTBot.getPost(Board, PostIndex=CurrentIndex - i)

            if ErrCode == PTT.ErrorCode.PostDeleted:
                # if LastPost.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
                #     if show:
                #         PTTBot.Log('文章被原 PO 刪掉了')
                # elif LastPost.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
                #     if show:
                #         PTTBot.Log('文章被版主刪掉了')
                # continue
                pass
            elif ErrCode != PTT.ErrorCode.Success:
                if show:
                    PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
                continue
            elif LastPost == None:
                continue
            elif LastPost.getDate() == None:
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