import time
import json
import getpass
import math
# from time import gmtime, strftime

from PTTLibrary import PTT
import Util

# False True
ask = False
publish = False
mail = False

# Test = False
author_list = dict()
ip_list = dict()
publish_content = None
new_line = '\r\n'
ptt_bot = PTT.Library(
    # LogLevel=PTT.LogLevel.DEBUG,
)


def PostHandler(Post):
    if Post is None:
        return

    DeleteStatus = Post.getDeleteStatus()
    if DeleteStatus != PTT.post_delete_status.NotDeleted:
        return

    global author_list
    global ip_list

    Author = Post.getAuthor()
    if Author is None:
        return
    if '(' in Author:
        Author = Author[:Author.find('(')].strip()

    # Author is OK

    IP = Post.getIP()
    if IP is None:
        return

    Title = Post.getTitle()
    if DeleteStatus == PTT.post_delete_status.ByAuthor:
        Title = '(本文已被刪除) [' + Author + ']'
    elif DeleteStatus == PTT.post_delete_status.ByModerator:
        Title = '(本文已被刪除) <' + Author + '>'
    elif DeleteStatus == PTT.post_delete_status.ByUnknow:
        # Title = '(本文已被刪除) <' + Author + '>'
        pass

    if Title is None:
        Title = ''
    # Title is OK

    if IP not in IPList:
        IPList[IP] = []

    if Author not in IPList[IP]:
        IPList[IP].append(Author)

    if Author not in AuthorList:
        AuthorList[Author] = []

    if IP not in AuthorList[Author]:
        AuthorList[Author].append(IP)

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

    global author_list
    global ip_list
    global new_line
    global ptt_bot
    global publish
    global ask
    global mail

    Util.PTTBot = PTTBot
    Util.post_search = None
    Util.current_board = Board
    Util.Moderators = Moderators

    global publish_content
    if PublishContent is None:

        PublishContent = '此內容由 IP 分析程式產生' + NewLine
        PublishContent += '由 CodingMan 透過 PTT Library 開發，' + NewLine * 2

        PublishContent += 'PTT Library: https://github.com/Truth0906/PTTLibrary' + NewLine
        PublishContent += '開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual' + NewLine
        PublishContent += 'IP 分析程式: https://github.com/Truth0906/PTTModeratorTool' + NewLine

    StartTime = time.time()
    AuthorList = dict()
    IPList = dict()
    CurrentDate = Util.get_date(DaysAgo)

    PTTBot.log(f'開始 {Board} 板 IP 分析')
    PTTBot.log(f'從 {CurrentDate} 開始分析')

    Start, _ = Util.find_post_rrange(DaysAgo, show=False)
    NewestIndex = PTTBot.getNewestIndex(
        PTT.IndexType.Board,
        Board=Board,
    )
    End = NewestIndex
    PTTBot.log('編號範圍 ' + str(Start) + ' ~ ' + str(End))

    ErrorPostList, DeleteCount = PTTBot.crawlBoard(
        PostHandler,
        Util.current_board,
        StartIndex=Start,
        EndIndex=End,
    )

    MultiPOResult = ''
    for Suspect, TitleAuthorList in AuthorList.items():

        if len(TitleAuthorList) <= 1:
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

    if MultiPOResult != '':
        Content += MultiPOResult

        MultiPOResult = MultiPOResult.strip()
        for line in MultiPOResult.split(NewLine):
            PublishContent += '    ' + line + NewLine
    else:
        Content += '◆ ' + CurrentDate + ' 無人違反多 PO 板規' + NewLine
        PublishContent += '    ' + '◆ ' + CurrentDate + ' 無人違反多 PO 板規' + NewLine

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

    ptt_bot.login(ID, Password, KickOtherLogin=True)

    for (current_board, ModeratorList, MaxPost) in SearchList:
        MultiPO(current_board, ModeratorList, MaxPost)

    publish_content += new_line + '內容如有失準，歡迎告知。' + new_line
    publish_content += 'CodingMan'

    if publish:
        CurrentDate = Util.get_date(1)

        ptt_bot.post('Test', CurrentDate + ' 多 PO 結果', publish_content, 1, 0)
        ptt_bot.log('在 Test 板發文成功')
    else:
        ptt_bot.log('取消備份')
    ptt_bot.logout()
