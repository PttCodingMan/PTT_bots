
import sys
import time
import json
import getpass

# from time import gmtime, strftime
sys.path.insert(0, 'D:/Git/PTTLibrary')
from PTTLibrary import PTT
import Util

List = {}

def PostHandler(Post):
    global List

    Author = Post.getAuthor()
    if '(' in Author:
        Author = Author[:Author.find('(')]
        Author = Author.rstrip()
    
    Title = Post.getTitle()
    Content = Post.getContent()
    DeleteStatus = Post.getDeleteStatus()

    if Author not in List:
        List[Author] = []
    
    if DeleteStatus == PTT.post_delete_status.NotDeleted:
        if '[公告]' in Title:
            return
    else:
        return
    if Content == None:
        return

    if not '───────────────────────' in Content:
        # 不正常文章 @@
        return
    Content = Content[Content.find('───────────────────────'):]
    Content = Content[Content.find('\n') + 1:]
    if not '※ 發信站:' in Content:
        print('沒有發信站')
        print(Title)
        print(Content)
        return
    
    Content = Content[:Content.find('※ 發信站:')]
    if Content.count('--') > 1:
        print(Content)
        ContentList = Content.split('\n')
        for i in range(len(ContentList)):
            line = ContentList[i]

            needRemove = False
            if '--' in line:
                for ii in range(1, 10):
                    if i + ii >= len(ContentList):
                        break
                    nextline = ContentList[i + ii]
                    if '※ 發信站:' in nextline:
                        needRemove = True
                        break
                
                if needRemove:
                    Content = Content[:Content.find(line)]
                    break
        print(Content)
    List[Author].append([Title, Content])
def countChinese(input):
    result = 0
    for char in input:
        if '\u4e00' <= char <= '\u9fff':
            result += 1
    return result
def countJP(input):
    result = 0
    for char in input:
        if '\u30a0' <= char <= '\u30ff':
            result += 1
        if '\u3040' <= char <= '\u309f':
            result += 1
    return result
def countEng(input):
    # isalpha
    result = 0
    LastCharInde = -1
    for i in range(len(input)):
        if LastCharInde != -1 and i <= LastCharInde:
            continue

        char = input[i]

        ii = i
        while char.isalpha():
            LastCharInde = ii
            ii += 1
            if ii >= len(input):
                break
            char = input[ii]
        if i != ii:
            result += 1
    
    return result

#unicode japanese hiragana 

if __name__ == '__main__':
    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')
    
    ptt_bot = PTT.Library(kickOtherLogin=False)
    Util.PTTBot = ptt_bot

    StartTime = time.time()

    ErrCode = ptt_bot.login(ID, Password)
    if ErrCode != PTT.ErrorCode.Success:
        ptt_bot.Log('登入失敗')
        sys.exit()
    
    NewestIndex, Todaty = Util.getToday()
    ptt_bot.Log('本日日期: >' + Todaty + '<')

    ptt_bot.Log('最新文章編號: ' + str(NewestIndex))
    TodayFirstIndex = Util.findFirstIndex(NewestIndex, Todaty)
    ptt_bot.Log('本日最舊文章編號: ' + str(TodayFirstIndex))

    YesterDayNewIndex, YesterDay = Util.getYesterDay(TodayFirstIndex)
    ptt_bot.Log('昨日日期: >' + YesterDay + '<')
    ptt_bot.Log('昨日最新文章編號: >' + str(YesterDayNewIndex) + '<')
    YesterDayOldIndex = Util.findFirstIndex(TodayFirstIndex - 1, YesterDay, show=False)
    ptt_bot.Log('昨日最舊文章編號: ' + str(YesterDayOldIndex))

    ErrCode, SuccessCount, DeleteCount = ptt_bot.crawlBoard(Util.current_board, PostHandler, StartIndex=YesterDayOldIndex, EndIndex=NewestIndex)
    if ErrCode != PTT.ErrorCode.Success:
        ptt_bot.Log('爬行失敗')
        sys.exit()
    
    ptt_bot.Log('爬行成功共 ' + str(SuccessCount) + ' 篇文章 共有 ' + str(DeleteCount) + ' 篇文章被刪除')

    # TargetWord = 'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ'
    # 把注音 ㄧ 拿掉，太容易搞混了
    TargetWord = 'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ'

    Result_1 = ''
    Result_2 = ''
    new_line = '\r\n'
    for Suspect, ContentList in List.items():
        for TitleContent in ContentList:
            
            Content = TitleContent[1]
            isTarget = False
            for Target in TargetWord:
                if Target in Content:
                    print('Find >' + Target + '<')
                    isTarget = True
                    break
            if isTarget:
                print('注音文 ======== ' + Suspect + ' ========')
                Title = TitleContent[0]
                print(Title)
                print(Content)

                Result_1 += '    ' + Suspect + '     □ ' + Title + new_line
            
            Count_Chinese = countChinese(Content)
            Count_JP = countJP(Content)
            Count_Eng = countEng(Content)

            Total = Count_Chinese + Count_JP + Count_Eng
            if Total < 20:
                print('20 字 ======== ' + Suspect + ' ========')
                Title = TitleContent[0]
                print(Title)
                print(Content)

                Result_2 += '    ' + Suspect + '     □ ' + Title + new_line

    EndTime = time.time()
