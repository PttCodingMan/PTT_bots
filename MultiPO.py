
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

SearchList = [
    ('Gossiping', ['Bignana', 'XXXXGAY'], 5),
    ('Wanted', ['LittleCalf', 'somisslove'], 3),
    ('give', ['gogin'], 3),
    ('HatePolitics', ['kero2377'], 5),
    ('Gamesale', ['mithralin'], 1),
]

Ask = False
Publish = True
Mail = True
# False True

AuthorList = dict()
IPList = dict()
PublishContent = None
NewLine = '\r\n'
PTTBot = PTT.Library()


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


def MultiPO(Board, Moderators, MaxPost):

    global AuthorList
    global IPList
    global NewLine
    global PTTBot
    global Publish
    global Ask
    global Mail
    global dayAgo

    Util.PTTBot = PTTBot
    Util.PostSearch = f'({Board})'
    Util.Moderators = Moderators

    global PublishContent
    if PublishContent is None:

        PublishContent = '此內容由抓多 PO 程式產生' + NewLine
        PublishContent += '由 CodingMan 透過 PTT Library 開發，' + NewLine * 2

        PublishContent += 'PTT Library: https://github.com/Truth0906/PTTLibrary' + NewLine
        PublishContent += '開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual' + NewLine
        PublishContent += '抓多 PO 程式: https://github.com/Truth0906/PTTModeratorTool' + NewLine

    StartTime = time.time()
    AuthorList = dict()
    IPList = dict()
    CurrentDate = Util.getDate(dayAgo)

    PTTBot.log(f'開始 {Board} 板昨天的多 PO 偵測')
    PTTBot.log('日期: ' + CurrentDate)
    Start, End = Util.findPostRrange(dayAgo, show=False)
    PTTBot.log('編號範圍 ' + str(Start) + ' ~ ' + str(End))

    ErrorPostList, DeleteCount = PTTBot.crawlBoard(
        PostHandler,
        PTT.IndexType.BBS,
        Util.Board,
        StartIndex=Start,
        EndIndex=End,
        SearchType=Util.PostSearchType,
        SearchCondition=Util.PostSearch,
        Query=True,
    )

    EndTime = time.time()

    MultiPOResult = ''
    for Suspect, TitleAuthorList in AuthorList.items():

        if len(TitleAuthorList) <= MaxPost:
            continue
        # print('=' * 5 + ' ' + Suspect + ' ' + '=' * 5)

        if MultiPOResult != '':
            MultiPOResult += NewLine
        for Title in TitleAuthorList:
            if not Title.startswith('R:'):
                MultiPOResult += CurrentDate + ' ' + \
                    Suspect + ' □ ' + Title + NewLine
            else:
                MultiPOResult += CurrentDate + ' ' + \
                    Suspect + ' ' + Title + NewLine

    IPResult = ''
    for IP, SuspectList in IPList.items():
        # print('len:', len(SuspectList))
        if len(SuspectList) <= MaxPost:
            continue

        # print('IP:', IP)
        IPResult += 'IP: ' + IP + NewLine

        for Line in SuspectList:
            # print('>   ' + CurrentDate + ' ' + Line)
            IPResult += CurrentDate + ' ' + Line + NewLine

    Title = CurrentDate + f' {Board} 板多 PO 結果'

    PublishContent += NewLine
    PublishContent += f'◆ {Board} 板多 PO 結果'

    Time = math.ceil(EndTime - StartTime)
    Min = int(Time / 60)
    Sec = int(Time % 60)

    Content = '此內容由抓多 PO 程式產生' + NewLine

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

    if MultiPOResult != '':
        Content += MultiPOResult

        MultiPOResult = MultiPOResult.strip()
        for line in MultiPOResult.split(NewLine):
            PublishContent += '    ' + line + NewLine
    else:
        Content += '◆ 無人違反多 PO 板規' + NewLine
        PublishContent += '    ' + '◆ 無人違反多 PO 板規' + NewLine

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
    
    dayAgo = 1

    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')

    PTTBot.login(ID, Password)

    for (Board, ModeratorList, MaxPost) in SearchList:
        MultiPO(Board, ModeratorList, MaxPost)

    PublishContent += NewLine + '歡迎其他板主來信新增檢查清單' + NewLine
    PublishContent += '內容如有失準，歡迎告知。' + NewLine
    PublishContent += 'CodingMan'

    if Publish:
        CurrentDate = Util.getDate(dayAgo)

        PTTBot.post('Test', CurrentDate + ' 多 PO 結果', PublishContent, 1, 0)
        PTTBot.log('在 Test 板發文成功')
    else:
        PTTBot.log('取消備份')
    PTTBot.logout()
