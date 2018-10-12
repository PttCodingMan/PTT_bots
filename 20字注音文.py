
import sys, os
import time
import json
import getpass
import codecs
import traceback
from datetime import date, timedelta
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
    
    if DeleteStatus == PTT.PostDeleteStatus.NotDeleted:
        if '[公告]' in Title:
            return
    else:
        return
    if Content == None:
        return
    
    # print(Content)
    # ───────────────────────────────────────
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
        # 有簽名檔移除
        if '-----' in Content:
            # APP 簽名檔
            Content = Content[:Content.rfind('-----')]
        else:
            # print(Content)
            Content = Content[:Content.rfind('--')]
            Content = Content[:Content.rfind('--')]
            # print(Content)

    List[Author].append([Title, Content])

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

    StartTime = time.time()

    ErrCode = PTTBot.login(ID, Password)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('登入失敗')
        sys.exit()
    
    NewestIndex, Todaty = Util.getToday()
    PTTBot.Log('本日日期: >' + Todaty + '<')

    PTTBot.Log('最新文章編號: ' + str(NewestIndex))
    TodayFirstIndex = Util.findFirstIndex(NewestIndex, Todaty)
    PTTBot.Log('本日最舊文章編號: ' + str(TodayFirstIndex))

    YesterDayNewIndex, YesterDay = Util.getYesterDay(TodayFirstIndex)
    PTTBot.Log('昨日日期: >' + YesterDay + '<')
    PTTBot.Log('昨日最新文章編號: >' + str(YesterDayNewIndex) + '<')
    YesterDayOldIndex = Util.findFirstIndex(TodayFirstIndex - 1, YesterDay, show=False)
    PTTBot.Log('昨日最舊文章編號: ' + str(YesterDayOldIndex))

    ErrCode, SuccessCount, DeleteCount = PTTBot.crawlBoard(Util.Board, PostHandler, StartIndex=YesterDayOldIndex, EndIndex=NewestIndex)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('爬行失敗')
        sys.exit()
    
    PTTBot.Log('爬行成功共 ' + str(SuccessCount) + ' 篇文章 共有 ' + str(DeleteCount) + ' 篇文章被刪除')

    # TargetWord = 'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ'
    # 把注音 ㄧ 拿掉，太容易搞混了
    TargetWord = 'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ'

    for Suspect, ContentList in List.items():
        # print('======== ' + Suspect + ' ========')
        for TitleContent in ContentList:
            
            Content = TitleContent[1]
            # print(Title)
            # print(Content)
            isTarget = False
            for Target in TargetWord:
                if Target in Content:
                    print('Find >' + Target + '<')
                    isTarget = True
                    break
            if isTarget:
                print('======== ' + Suspect + ' ========')
                Title = TitleContent[0]
                print(Title)
                print(Content)
        
    EndTime = time.time()
