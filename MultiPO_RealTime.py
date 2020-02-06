
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

ask = False
publish = False
mail = True
# False True

author_list = dict()
ip_list = dict()
publish_content = None
new_line = '\r\n'


def PostHandler(Post):
    if Post is None:
        return
    global author_list
    global ip_list

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


def MultiPO(Board, Moderators, MaxPost, Handler):

    global author_list
    global ip_list
    global new_line
    global ptt_bot
    global publish
    global ask
    global mail
    global dayAgo

    Util.PTTBot = PTTBot
    Util.post_search = f'({Board})'
    Util.Moderators = Moderators

    global publish_content
    if PublishContent is None:

        PublishContent = '此內容由抓多 PO 程式產生' + NewLine
        PublishContent += '由 CodingMan 透過 PTT Library 開發，' + NewLine * 2

        PublishContent += 'PTT Library: https://github.com/Truth0906/PTTLibrary' + NewLine
        PublishContent += '開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual' + NewLine
        PublishContent += '抓多 PO 程式: https://github.com/Truth0906/PTTModeratorTool' + NewLine

    StartTime = time.time()
    AuthorList = dict()
    IPList = dict()
    CurrentDate = Util.get_date(dayAgo)

    # PTTBot.log(f'開始 {Board} 板昨天的多 PO 偵測')
    # PTTBot.log('日期: ' + CurrentDate)
    Start, End = Util.find_post_rrange(dayAgo, show=False)
    PTTBot.log('編號範圍 ' + str(Start) + ' ~ ' + str(End))

    ErrorPostList, DeleteCount = PTTBot.crawlBoard(
        PostHandler,
        PTT.IndexType.BBS,
        Util.current_board,
        StartIndex=Start,
        EndIndex=End,
        SearchType=Util.post_search_type,
        SearchCondition=Util.post_search,
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
            MultiPOResult += CurrentDate + ' ' + \
                Suspect + ' □ ' + Title + NewLine

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

    if Handler is None:
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

    else:
        Handler(CurrentDate, AuthorList, IPList, MaxPost, Min, Sec)


HatePoliticsList = dict()


def HatePoliticsHandler(CurrentDate, AuthorList, IPList, MaxPost, Min, Sec):

    global new_line
    global HatePoliticsList

    MultiPOResult = ''
    PublishContent = ''

    CurrentList = dict()
    for Suspect, TitleAuthorList in AuthorList.items():

        if len(TitleAuthorList) <= MaxPost:
            continue

        if Suspect in HatePoliticsList:
            continue

        MultiPOResult = ''

        for Title in TitleAuthorList:
            MultiPOResult += CurrentDate + ' ' + \
                Suspect + ' □ ' + Title + NewLine

        # print(f'1-> {MultiPOResult} ====')
        PublishContent = ''
        MultiPOResult = MultiPOResult.strip()
        for line in MultiPOResult.split(NewLine):
            PublishContent += '    ' + line + NewLine

        # print(f'2-> {PublishContent} ====')

        CurrentList[Suspect] = PublishContent

    for Suspect in CurrentList:
        # print(Suspect)
        # print(SuspectList[Suspect])

        Sample = f'''
一、檢舉人ID：CodingMan

二、被檢舉人ID：{Suspect}

三、違反板規： ※此項請直接複製完整條文貼上，切勿只寫板規編號※

    第二章  文章分類

    17.每日發文/回文上限5篇，禁止手動置底相似文章 違者超貼文章刪除

四、違規文章代碼與說明：

'''
        Title = f'多篇文章 {Suspect} 政黑板規2-17'
        Content = Sample + CurrentList[Suspect]
        Content = Content.replace('\r\n', '==NewLine==')
        Content = Content.replace('\n', NewLine)
        Content = Content.replace('==NewLine==', '\r\n')

        print(Title)
        print(Content)
        print('=' * 50)

        # global PTTBot

        # PTTBot.post(
        #     # 'HateP_Picket',
        #     'Test',
        #     Title,
        #     Content,
        #     1,
        #     0
        # )

    if len(CurrentList) != 0:
        HatePoliticsList.update(CurrentList)
        CurrentDate = Util.get_date(dayAgo).replace('/', '')
        with open(f'HatePoliticsList_{CurrentDate}.txt', 'w', encoding='utf8') as File:
            json.dump(HatePoliticsList, File, indent=4, ensure_ascii=False)
    else:
        print('沒有結果')


if __name__ == '__main__':

    from time import gmtime, strftime

    SearchList = [
        # ('Gossiping', ['Bignana', 'XXXXGAY'], 5, None),
        # ('Wanted', ['LittleCalf'], 3, None),
        # ('give', ['gogin'], 3, None),
        ('HatePolitics', ['Neptunium', 'mark2165',
                          'kero2377'], 5, HatePoliticsHandler),
    ]

    dayAgo = 0

    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')

    try:
        CurrentDate = Util.get_date(dayAgo).replace('/', '')
        with open(f'HatePoliticsList_{CurrentDate}.txt', encoding='utf8') as File:
            HatePoliticsList = json.load(File)
    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)
        print('無法讀取 HatePoliticsList.txt')
        HatePoliticsList = dict()
    
    LastDate = Util.get_date(dayAgo)

    ptt_bot = PTT.Library(
        # LogLevel=PTT.LogLevel.TRACE
    )
    try:
        ptt_bot.login(
            ID,
            Password,
            KickOtherLogin=True
        )
    except PTT.Exceptions.LoginError:
        ptt_bot.log('登入失敗')
        sys.exit()
    except PTT.Exceptions.ConnectError:
        ptt_bot.log('登入失敗')
        sys.exit()
    except PTT.Exceptions.ConnectionClosed:
        ptt_bot.log('登入失敗')
        sys.exit()

    Index = 0
    LastIndex = 0
    while True:
        while LastIndex == Index:
            Time = strftime('%H:%M:%S')
            try:
                CurrentDate = Util.get_date(dayAgo)
                if CurrentDate != LastDate:
                    # 新的一天!!!清空清單
                    ptt_bot.logout()

                    print('半夜休息中')

                    # 暫停六小時
                    time.sleep(60 * 60 * 6)
                    print('重新上工!!')
                    LastDate = CurrentDate
                    HatePoliticsList = dict()

                    ptt_bot.login(ID, Password)

                Index = ptt_bot.getNewestIndex(
                    PTT.IndexType.BBS,
                    Board='ALLPOST',
                    SearchType=PTT.PostSearchType.Keyword,
                    SearchCondition='(HatePolitics)',
                )
            except PTT.Exceptions.ConnectionClosed:
                while True:
                    try:
                        ptt_bot.login(
                            ID,
                            Password,
                            KickOtherLogin=True
                        )
                        break
                    except PTT.Exceptions.LoginError:
                        ptt_bot.log('登入失敗')
                        time.sleep(1)
                    except PTT.Exceptions.ConnectError:
                        ptt_bot.log('登入失敗')
                        time.sleep(1)
                    except PTT.Exceptions.ConnectionClosed:
                        ptt_bot.log('登入失敗')
                        time.sleep(1)
            except PTT.Exceptions.UseTooManyResources:
                while True:
                    try:
                        ptt_bot.login(
                            ID,
                            Password,
                            KickOtherLogin=True
                        )
                        break
                    except PTT.Exceptions.LoginError:
                        ptt_bot.log('登入失敗')
                        time.sleep(1)
                    except PTT.Exceptions.ConnectError:
                        ptt_bot.log('登入失敗')
                        time.sleep(1)
            print(f'{Time} 最新編號 {Index}', end='\r')
            if LastIndex != Index:
                LastIndex = Index
                print(f'{Time} 最新編號 {Index}')
                break
            LastIndex = Index
            time.sleep(5)

        for (current_board, ModeratorList, MaxPost, Handler) in SearchList:
            MultiPO(current_board, ModeratorList, MaxPost, Handler)

    ptt_bot.logout()
