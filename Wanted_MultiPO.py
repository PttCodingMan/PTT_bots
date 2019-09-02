
import sys
import os
import time
import json
import getpass
import codecs
import traceback
from datetime import date, timedelta
# from time import gmtime, strftime

from PTTLibrary import PTT
import Util

Test = False


def PostHandler(Post):
    if Post is None:
        return
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
    elif DeleteStatus == PTT.PostDeleteStatus.ByUnknow:
        # Title = '(本文已被刪除) <' + Author + '>'
        pass

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
            IPList[IP].append(Author + '     □ ' + Title)

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

    PTTBot = PTT.Library(
        # LogLevel=PTT.Log.Level.DEBUG
    )
    Util.PTTBot = PTTBot

    while True:
        try:
            # HowManyDay = int(input('想從幾天前開始抓多PO?\n: '))
            HowManyDay = 1
            if HowManyDay < 1 or 30 < HowManyDay:
                PTTBot.log('輸入錯誤，請重新輸入 1 ~ 30')
                continue
            break
        except:
            PTTBot.log('輸入錯誤，請重新輸入')
            continue

    ErrCode = PTTBot.login(ID, Password, KickOtherLogin=True)

    PTTBot.log('從 ' + str(HowManyDay) + ' 天前開始抓多PO')

    Result = ''
    NewLine = '\r\n'

    # global AuthorList

    for dayAgo in range(HowManyDay, 0, -1):

        StartTime = time.time()
        AuthorList = dict()
        IPList = dict()
        CurrentDate = Util.getDate(dayAgo)

        PTTBot.log('開始 ' + str(dayAgo) + ' 天前的多PO偵測')
        PTTBot.log('日期: ' + CurrentDate)
        Start, End = Util.findPostRrange(dayAgo, show=False)
        PTTBot.log('編號範圍 ' + str(Start) + ' ~ ' + str(End))

        # sys.exit()

        if not Test:

            ErrorPostList, DeleteCount = PTTBot.crawlBoard(
                PostHandler,
                Util.Board,
                StartIndex=Start,
                EndIndex=End,
                SearchType=Util.PostSearchType,
                SearchCondition=Util.PostSearch
            )

        else:

            for PostIndex in range(Start, End + 1):
                ErrCode, Post = PTTBot.getPost(
                    Util.Board, PostIndex=PostIndex, SearchType=Util.PostSearchType, SearchCondition=Util.PostSearch)
                if ErrCode == PTT.ErrorCode.PostDeleted:
                    if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
                        # PTTBot.log('文章被原 PO 刪掉了')
                        pass
                    elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
                        # PTTBot.log('文章被版主刪掉了')
                        pass
                    elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByUnknow:
                        # PTTBot.log('文章被刪掉了 in ALLPOST')
                        pass

                    PostHandler(Post)
                    continue
                elif ErrCode != PTT.ErrorCode.Success:
                    PTTBot.log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
                    PostHandler(Post)
                    sys.exit()
                    continue

                PostHandler(Post)

        MultiPOResult = ''
        for Suspect, TitleAuthorList in AuthorList.items():

            if len(TitleAuthorList) < 4:
                continue
            # print('=' * 5 + ' ' + Suspect + ' ' + '=' * 5)

            if MultiPOResult != '':
                MultiPOResult += NewLine
            for Title in TitleAuthorList:
                MultiPOResult += '>   ' + CurrentDate + ' ' + \
                    Suspect + '     □ ' + Title + NewLine

        IPResult = ''
        for IP, SuspectList in IPList.items():
            # print('len:', len(SuspectList))
            if len(SuspectList) <= 3:
                continue

            # print('IP:', IP)
            IPResult += 'IP: ' + IP + NewLine

            for Line in SuspectList:
                # print('>   ' + CurrentDate + ' ' + Line)
                IPResult += '>   ' + CurrentDate + ' ' + Line + NewLine

        EndTime = time.time()

        Title = CurrentDate + ' 汪踢板多PO結果'

        Content = '此封信內容由汪踢自動抓多 PO 程式產生' + NewLine + '共耗時 ' + \
            str(int(EndTime - StartTime)) + ' 秒執行完畢' + NewLine * 2
        Content += '此程式是由 CodingMan 透過 PTT Library 開發，' + NewLine * 2
        Content += 'PTT Library: https://github.com/Truth0906/PTTLibrary' + NewLine
        Content += '開發指南: https://hackmd.io/@CodingMan/PTTLibraryManual' + NewLine * 2
        Content += '蒐集範圍為ALLPOST搜尋(Wanted)情況下編號 ' + \
            str(Start) + ' ~ ' + str(End) + NewLine + NewLine

        if MultiPOResult != '':
            Content += MultiPOResult
        else:
            Content += CurrentDate + '無人違反多PO板規' + NewLine

        if IPResult != '':
            Content += IPResult
        else:
            Content += NewLine + '沒有發現特定 IP 有四篇以上文章' + NewLine

        Content += NewLine + '內容如有失準，歡迎告知。' + NewLine
        MailContent = Content
        Content += '此訊息同步發送給 ' + ' '.join(Util.Moderators) + NewLine
        Content += NewLine
        Content += ID

        print(Title)
        print(Content)

        # SendMail = input('請問寄出通知信給板主群？[Y/n] ').lower()
        # SendMail = (SendMail == 'y' or SendMail == '')
        SendMail = True
        TestBackup = True
        # False True
        if SendMail:
            for Moderator in Util.Moderators:
                PTTBot.mail(Moderator, Title, Content, 0)
                PTTBot.log('寄信給 ' + Moderator + ' 成功')
        else:
            PTTBot.log('取消寄信')

        if TestBackup:
            PTTBot.post('Test', Title, MailContent, 1, 1)
            PTTBot.log('在 Test 板發文成功')
    PTTBot.logout()
