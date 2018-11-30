
import sys, os
import time
import json
import getpass
import codecs
import traceback
from datetime import date, timedelta
# from time import gmtime, strftime

from PTTLibrary import PTT
import Util

Test = True


def PostHandler(Post):
    global AuthorList
    global IPList

    Author = Post.getAuthor()
    if '(' in Author:
        Author = Author[:Author.find('(')]
        Author = Author.rstrip()
    # Author is OK
    Title = Post.getTitle()
    DeleteStatus = Post.getDeleteStatus()
    IP = Post.getIP()

    if DeleteStatus == PTT.PostDeleteStatus.ByAuthor:
        Title = '(本文已被刪除) [' + Author + ']'
    elif DeleteStatus == PTT.PostDeleteStatus.ByModerator:
        Title = '(本文已被刪除) <' + Author + '>'
    if Title is None:
        Title = ''
    # Title is OK
    
    if Author not in AuthorList:
        AuthorList[Author] = []

    if IP is not None and IP not in IPList:
        IPList[IP] = []
        
    if DeleteStatus == PTT.PostDeleteStatus.NotDeleted:
        if '[公告]' in Title:
            return
        if IP is not None:
            IPList[IP].append((Author, Title))

    AuthorList[Author].append(Title)
    

if __name__ == '__main__':
    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')
    
    PTTBot = PTT.Library(kickOtherLogin=False)
    Util.PTTBot = PTTBot

    while True:
        try:
            # HowManyDay = int(input('想從幾天前開始抓多PO?\n: '))
            HowManyDay = 1
            if HowManyDay < 1 or 30 < HowManyDay:
                PTTBot.Log('輸入錯誤，請重新輸入 1 ~ 30')
                continue
            break
        except:
            PTTBot.Log('輸入錯誤，請重新輸入')
            continue

    ErrCode = PTTBot.login(ID, Password)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('登入失敗')
        sys.exit()

    PTTBot.Log('從 ' + str(HowManyDay) + ' 天前開始抓多PO')

    Result = ''
    NewLine = '\r\n'

    # global AuthorList

    for dayAgo in range(HowManyDay, 0, -1):

        StartTime = time.time()
        AuthorList = dict()
        IPList = dict()
        CurrentDate = Util.getDate(dayAgo)
        
        PTTBot.Log('開始 ' + str(dayAgo) + ' 天前的多PO偵測')
        PTTBot.Log('日期: ' + CurrentDate)
        Start, End = Util.findPostRrange(dayAgo, show=False)
        PTTBot.Log('編號範圍 ' + str(Start) + ' ~ ' + str(End))

        if not Test:

            ErrCode, SuccessCount, DeleteCount = PTTBot.crawlBoard(
                Util.Board, PostHandler, 
                StartIndex=Start, EndIndex=End)
            if ErrCode != PTT.ErrorCode.Success:
                PTTBot.Log('爬行失敗')
                sys.exit()
        
        else:

            for PostIndex in range(Start, End + 1):
                print(PostIndex)
                ErrCode, Post = PTTBot.getPost(Util.Board, PostIndex=PostIndex)

                PostHandler(Post)
            
        Result = ''
        for Suspect, TitleAuthorList in AuthorList.items():
            
            if len(TitleAuthorList) < 4:
                continue
            # print('=' * 5 + ' ' + Suspect + ' ' + '=' * 5)

            Result += NewLine
            for Title in TitleAuthorList:
                Result += '>   ' + CurrentDate + ' ' + Suspect + '     □ ' + Title + NewLine
        
        for IP, SuspectList in IPList.items():
            # print('len:', len(SuspectList))
            if len(SuspectList) <= 2:
                continue
            
            print('IP:', IP)
        
            for Author, Title in SuspectList:
                print('>   ' + CurrentDate + ' ' + Suspect + '     □ ' + Title)
        
        EndTime = time.time()
        
        Title = CurrentDate + ' 汪踢板多PO結果'

        Content = '此封信內容由汪踢自動抓多 PO 程式產生' + NewLine + '共耗時 ' + str(int(EndTime - StartTime)) + ' 秒執行完畢' + NewLine
        Content += '蒐集範圍為編號 ' + str(Start) + ' ~ ' + str(End) + NewLine + NewLine

        if Result != '':
            Content += Result
        else:
            Content += CurrentDate + '無人違反多PO板規'
        Content += NewLine + NewLine + '內容如有失準，歡迎告知。' + NewLine
        MailContent = Content
        Content += '此訊息同步發送給 ' + ' '.join(Util.Moderators) + NewLine
        Content += NewLine
        Content += ID

        print(Title)
        print(Content)

        # SendMail = input('請問寄出通知信給板主群？[Y/n] ').lower()
        # SendMail = (SendMail == 'y' or SendMail == '')
        SendMail = False
        TestBackup = False
        # False True
        if SendMail:
            for Moderator in Util.Moderators:
                ErrCode = PTTBot.mail(Moderator, Title, Content, 0)
                if ErrCode == PTT.ErrorCode.Success:
                    PTTBot.Log('寄信給 ' + Moderator + ' 成功')
                else:
                    PTTBot.Log('寄信給 ' + Moderator + ' 失敗')
        else:
            PTTBot.Log('取消寄信')
        
        if TestBackup:
            ErrCode = PTTBot.post('Test', Title, MailContent, 1, 1)
            if ErrCode == PTT.ErrorCode.Success:
                PTTBot.Log('在 Test 板發文成功')
            elif ErrCode == PTT.ErrorCode.NoPermission:
                PTTBot.Log('發文權限不足')
            else:
                PTTBot.Log('在 Test 板發文失敗')
    PTTBot.logout()