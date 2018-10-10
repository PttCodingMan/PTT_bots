
import sys, os
import time
import json
import getpass
import codecs
import traceback
from datetime import date, timedelta
# from time import gmtime, strftime

from PTTLibrary import PTT

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
            if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
                PTTBot.Log('文章被原 PO 刪掉了')
            elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
                PTTBot.Log('文章被版主刪掉了')
            continue
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
            continue
        
        NewestIndex = NewestIndex - i

        break
    
    # print(Post.getDate())
    result = Post.getDate()[:10]
    return NewestIndex, result

def getYesterDay(TodayOldestIndex):

    for i in range(1, 20):
    
        ErrCode, Post = PTTBot.getPost(Board, PostIndex=TodayOldestIndex - i)

        if ErrCode == PTT.ErrorCode.PostDeleted:
            if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
                PTTBot.Log('文章被原 PO 刪掉了')
            elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
                PTTBot.Log('文章被版主刪掉了')
            continue
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
            continue
        
        break
    result = Post.getDate()[:10]
    return result

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
            
            CurrentIndex += 1
            continue
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
            CurrentIndex += 1
            continue
        
        for i in range(1, 20):

            ErrCode, LastPost = PTTBot.getPost(Board, PostIndex=CurrentIndex - i)

            if ErrCode == PTT.ErrorCode.PostDeleted:
                if LastPost.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
                    if show:
                        PTTBot.Log('文章被原 PO 刪掉了')
                elif LastPost.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
                    if show:
                        PTTBot.Log('文章被版主刪掉了')
                continue
            elif ErrCode != PTT.ErrorCode.Success:
                if show:
                    PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
                continue
            if show:
                PTTBot.Log('找到上一篇: ' + str(CurrentIndex - i))
            break
        CurrentToday = Post.getDate()[:10]
        LastCurrentToday = LastPost.getDate()[:10]

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

List = {}

def PostHandler(Post):
    global List
    # 6 +   9/24 DuDuCute     □ [徵求] 聊聊                         (Wanted)
    Author = Post.getAuthor()
    Title = Post.getTitle()
    DeleteStatus = Post.getDeleteStatus()
    ID = Post.getID()


    if Author not in List:
        List[Author] = []
    
    if DeleteStatus == PTT.PostDeleteStatus.NotDeleted:
        if '[公告]' in Title:
            return
    elif DeleteStatus == PTT.PostDeleteStatus.ByAuthor:
        Title = '(本文已被刪除) [' + Author + ']'
    elif DeleteStatus == PTT.PostDeleteStatus.ByModerator:
        Title = '(本文已被刪除) <' + Author + '>'

    List[Author].append(Title)

if __name__ == '__main__':
    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')
    
    PTTBot = PTT.Library()

    StartTime = time.time()

    ErrCode = PTTBot.login(ID, Password)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('登入失敗')
        sys.exit()
    
    NewestIndex, Todaty = getToday()
    PTTBot.Log('Todaty: >' + Todaty + '<')

    PTTBot.Log('最新文章編號: ' + str(NewestIndex))
    TodayFirstIndex = findFirstIndex(NewestIndex, Todaty)
    PTTBot.Log('本日最舊文章編號: ' + str(TodayFirstIndex))

    YesterDay = getYesterDay(TodayFirstIndex)
    PTTBot.Log('YesterDay: >' + YesterDay + '<')
    YesterDayIndex = findFirstIndex(TodayFirstIndex - 1, YesterDay, show=False)
    PTTBot.Log('昨日最舊文章編號: ' + str(YesterDayIndex))

    ErrCode, SuccessCount, DeleteCount = PTTBot.crawlBoard(Board, PostHandler, StartIndex=YesterDayIndex, EndIndex=TodayFirstIndex - 1)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('爬行失敗')
        sys.exit()
    
    PTTBot.Log('爬行成功共 ' + str(SuccessCount) + ' 篇文章 共有 ' + str(DeleteCount) + ' 篇文章被刪除')
    yesterday = date.today() - timedelta(1)

    Date = yesterday.strftime("%m/%d")

    Result = ''
    NewLine = '\r\n'
    for Suspect, TitleList in List.items():
        # 6 +   9/24 DuDuCute     □ [徵求] 聊聊                         (Wanted)
        if len(TitleList) < 4:
            continue
        # print('=' * 5 + ' ' + Suspect + ' ' + '=' * 5)
        Suspect = Suspect[:Suspect.find('(')]
        Suspect.rstrip()

        Result += NewLine
        for Title in TitleList:
            # print('>   ' + Date + ' ' + Suspect + '     □ ' + Title)
            Result += '>   ' + Date + ' ' + Suspect + '     □ ' + Title + NewLine
        
    EndTime = time.time()
    # 
    if Result != '':
        Title = Date + ' 汪踢板多PO結果'
        Content = '此封信內容由汪踢自動抓多 PO 程式產生' + NewLine + '共耗時 ' + str(int(EndTime - StartTime)) + ' 秒執行完畢' + NewLine + NewLine
        Content += Result
        Content += '\r\r內容如有失準，歡迎告知。' + NewLine
        Content += '此訊息同步發送給 ' + ' '.join(Moderators) + NewLine
        Content += NewLine
        Content += ID

        print(Title)
        print(Content)

        SendMail = input('請問寄出通知信給板主群？[Y/n] ').lower()
        SendMail = (SendMail == 'y' or SendMail == '')

        if SendMail:
            for Moderator in Moderators:
                ErrCode = PTTBot.mail(Moderator, Title, Content, 0)
                if ErrCode == PTT.ErrorCode.Success:
                    PTTBot.Log('寄信給 ' + Moderator + ' 成功')
                else:
                    PTTBot.Log('寄信給 ' + Moderator + ' 失敗')
        else:
            PTTBot.Log('取消寄信')
    else:
        print('無人違規')
    PTTBot.logout()