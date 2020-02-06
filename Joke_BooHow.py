
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

if __name__ == '__main__':

    from time import gmtime, strftime

    dayAgo = 0

    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')

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

    run = True

    Index = 0
    LastIndex = 0
    while run:
        LastIndex = Index
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
                    Board='joke',
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
            if LastIndex != Index and LastIndex != 0:
                print(f'{Time} 最新編號 {Index}')
                break
            LastIndex = Index
            try:
                time.sleep(5)
            except:
                run = False
                break
        if not run:
            break

        print(Index)
        print(LastIndex)
        print(f'{Index - LastIndex} 篇新文章')

        for i in range(LastIndex + 1, Index + 1):
            print(f'偵測編號 {i} 文章')

            Post = ptt_bot.getPost(
                'joke',
                PostIndex=i
            )

            if 'how' in Post.getContent().lower():
                print('Find how!!!')
                ptt_bot.push(
                    'joke',
                    PostIndex=i,
                    PushType=PTT.PushType.Boo,
                    PushContent='垃圾號欠噓'
                )

        print('=' * 50)

    ptt_bot.logout()
