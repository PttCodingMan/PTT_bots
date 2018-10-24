
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

List = {}

def PostHandler(Post):
    global List

    Author = Post.getAuthor()
    if '(' in Author:
        Author = Author[:Author.find('(')]
        Author = Author.rstrip()
    
    Title = Post.getTitle()
    DeleteStatus = Post.getDeleteStatus()

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
    PTTBot.Log('本日第一篇文章編號: ' + str(TodayFirstIndex))

    YesterDayNewIndex, YesterDay = Util.getYesterDay(TodayFirstIndex)
    PTTBot.Log('昨日日期: >' + YesterDay + '<')
    PTTBot.Log('昨日最後一篇文章編號: >' + str(YesterDayNewIndex) + '<')
    YesterDayOldIndex = Util.findFirstIndex(TodayFirstIndex - 1, YesterDay, show=True)
    PTTBot.Log('昨日第一篇文章編號: ' + str(YesterDayOldIndex))

    ErrCode, SuccessCount, DeleteCount = PTTBot.crawlBoard(Util.Board, PostHandler, StartIndex=YesterDayOldIndex, EndIndex=YesterDayNewIndex)
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

        Result += NewLine
        for Title in TitleList:
            # print('>   ' + Date + ' ' + Suspect + '     □ ' + Title)
            Result += '>   ' + Date + ' ' + Suspect + '     □ ' + Title + NewLine
        
    EndTime = time.time()
    # 
    Title = Date + ' 汪踢板多PO結果'
    Content = '此封信內容由汪踢自動抓多 PO 程式產生' + NewLine + '共耗時 ' + str(int(EndTime - StartTime)) + ' 秒執行完畢' + NewLine
    Content += '蒐集範圍為編號 ' + str(YesterDayOldIndex) + ' ~ ' + str(YesterDayNewIndex) + NewLine + NewLine

    if Result != '':
        Content += Result
    else:
        Content += '昨天無人違反多PO板規'
    Content += NewLine + NewLine + '內容如有失準，歡迎告知。' + NewLine
    Content += '此訊息同步發送給 ' + ' '.join(Util.Moderators) + NewLine
    Content += NewLine
    Content += ID

    print(Title)
    print(Content)

    SendMail = input('請問寄出通知信給板主群？[Y/n] ').lower()
    SendMail = (SendMail == 'y' or SendMail == '')

    if SendMail:
        for Moderator in Util.Moderators:
            ErrCode = PTTBot.mail(Moderator, Title, Content, 0)
            if ErrCode == PTT.ErrorCode.Success:
                PTTBot.Log('寄信給 ' + Moderator + ' 成功')
            else:
                PTTBot.Log('寄信給 ' + Moderator + ' 失敗')
    else:
        PTTBot.Log('取消寄信')
    PTTBot.logout()