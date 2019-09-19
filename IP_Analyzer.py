
import sys
import os
import time
import json
import getpass
import codecs
import traceback
import math
from datetime import date, timedelta
# from time import gmtime, strftime

from PTTLibrary import PTT
import Util

# False True
Ask = False
Publish = False
Mail = False

# Test = False
AuthorList = dict()
IPList = dict()
PublishContent = None
NewLine = '\r\n'
PTTBot = PTT.Library(
    # LogLevel=PTT.LogLevel.DEBUG,
)


def PostHandler(Post):
    if Post is None:
        return
    global AuthorList
    global IPList

    Author = Post.getAuthor()
    if '(' in Author:
        Author = Author[:Author.find('(')].strip()

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

    # print(f'==>{Author}<==>{Title}<')

    if IP is not None and IP not in IPList:
        IPList[IP] = []

    if DeleteStatus == PTT.PostDeleteStatus.NotDeleted:
        if '[公告]' in Title:
            return
        if IP is not None:
            if Author not in IPList[IP]:
                IPList[IP].append(Author)

    # Post is ok

    if Post.getPushList() is None:
        return

    for Push in Post.getPushList():

        Author = Push.getAuthor()
        IP = Push.getIP()

        if IP is None:
            continue

        if IP not in IPList:
            IPList[IP] = []
        if Author in IPList[IP]:
            continue

        IPList[IP].append(Author)


def MultiPO(Board, Moderators, DaysAgo):

    global AuthorList
    global IPList
    global NewLine
    global PTTBot
    global Publish
    global Ask
    global Mail

    Util.PTTBot = PTTBot
    Util.PostSearch = None
    Util.Board = Board
    Util.Moderators = Moderators

    global PublishContent
    if PublishContent is None:

        PublishContent = '此內容由 IP 分析程式產生' + NewLine
        PublishContent += '由 CodingMan 透過 PTT Library 開發，' + NewLine * 2

        PublishContent += 'PTT Library: https://github.com/Truth0906/PTTLibrary' + NewLine
        PublishContent += '開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual' + NewLine
        PublishContent += 'IP 分析程式: https://github.com/Truth0906/PTTModeratorTool' + NewLine

    StartTime = time.time()
    AuthorList = dict()
    IPList = dict()
    CurrentDate = Util.getDate(DaysAgo)

    PTTBot.log(f'開始 {Board} 板 IP 分析')
    PTTBot.log(f'從 {CurrentDate} 開始分析')

    Start, _ = Util.findPostRrange(DaysAgo, show=False)
    NewestIndex = PTTBot.getNewestIndex(
        PTT.IndexType.Board,
        Board=Board,
    )
    End = NewestIndex
    PTTBot.log('編號範圍 ' + str(Start) + ' ~ ' + str(End))

    ErrorPostList, DeleteCount = PTTBot.crawlBoard(
        PostHandler,
        Util.Board,
        StartIndex=Start,
        EndIndex=End,
    )

    IPResult = ''
    for IP, SuspectList in IPList.items():
        # print('len:', len(SuspectList))
        if len(SuspectList) <= 1:
            continue

        # print('IP:', IP)
        IPResult += 'IP: ' + IP + NewLine

        for Line in SuspectList:
            # print('>   ' + CurrentDate + ' ' + Line)
            IPResult += CurrentDate + ' ' + Line + NewLine

    EndTime = time.time()

    Title = CurrentDate + f' {Board} 板 IP 分析結果'

    PublishContent += NewLine
    PublishContent += '◆ ' + CurrentDate + f' {Board} 板 IP 分析結果'

    Time = math.ceil(EndTime - StartTime)
    Min = int(Time / 60)
    Sec = int(Time % 60)

    Content = '此內容由自動抓多 PO 程式產生' + NewLine

    Content += '共耗時'
    PublishContent += '共耗時'
    if Min > 0:
        Content += f' {Min} 分'
        PublishContent += f' {Min} 分'
    Content += f' {Sec} 秒執行完畢' + NewLine * 2
    PublishContent += f' {Sec} 秒執行完畢' + NewLine * 2

    Content += '此程式是由 CodingMan 透過 PTT Library 開發，' + NewLine * 2
    Content += f'蒐集範圍為 ALLPOST 搜尋 ({Board}) 情況下編號 ' + \
        str(Start) + ' ~ ' + str(End) + NewLine
    Content += f'共 {End - Start + 1} 篇文章' + NewLine * 2

    PublishContent += f'    蒐集範圍為 ALLPOST 搜尋 ({Board}) 情況下編號 ' + \
        str(Start) + ' ~ ' + str(End) + NewLine
    PublishContent += f'    共 {End - Start + 1} 篇文章' + NewLine * 2

    if IPResult != '':
        Content += IPResult
        IPResult = IPResult.strip()
        for line in IPResult.split(NewLine):
            PublishContent += '    ' + line + NewLine
    else:
        Content += NewLine + f'◆ 沒有發現特定 IP 有 {MaxPost + 1} 篇以上文章' + NewLine
        PublishContent += NewLine + \
            f'    ◆ 沒有發現特定 IP 有 {MaxPost + 1} 篇以上文章' + NewLine

    Content += NewLine + '內容如有失準，歡迎告知。' + NewLine
    Content += '此訊息同步發送給 ' + ' '.join(Util.Moderators) + NewLine
    Content += NewLine
    Content += ID

    print(Title)
    print(Content)

    if Ask:
        Choise = input('要發佈嗎? [Y]').lower()
        Publish = (Choise == 'y') or (Choise == '')

    if Mail:
        for Moderator in Util.Moderators:
            PTTBot.mail(Moderator, Title, Content, 0)
            PTTBot.log('寄信給 ' + Moderator + ' 成功')
    else:
        PTTBot.log('取消寄信')


if __name__ == '__main__':

    SearchList = [
        # ('Gossiping', ['Bignana'], 1),
        ('Wanted', ['gogin'], 1),
        ('HatePolitics', ['Neptunium', 'mark2165', 'kero2377'], 1),
    ]

    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')

    PTTBot.login(ID, Password, KickOtherLogin=True)

    for (Board, ModeratorList, MaxPost) in SearchList:
        MultiPO(Board, ModeratorList, MaxPost)

    PublishContent += NewLine + '內容如有失準，歡迎告知。' + NewLine
    PublishContent += 'CodingMan'

    if Publish:
        CurrentDate = Util.getDate(1)

        PTTBot.post('Test', CurrentDate + ' 多 PO 結果', PublishContent, 1, 0)
        PTTBot.log('在 Test 板發文成功')
    else:
        PTTBot.log('取消備份')
    PTTBot.logout()
