
import sys
import os
import time
import json
import random
import traceback
import PTTLibrary
import threading

from PTTLibrary import PTT


def getPW():
    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        print('Please note PTT ID and Password in Account.txt')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ID, Password


if __name__ == '__main__':
    os.system('cls')
    PTTBot = PTT.Library(
        # LogLevel=PTT.LogLevel.TRACE
    )

    ID, Password = getPW()

    try:
        PTTBot.login(
            ID,
            Password,
            # KickOtherLogin=True
        )
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()

    TargetPreTime = '23:59'

    Board = 'Wanted'
    Title = '2020 第一篇'
    Content = '''
汪踢!!新年快樂!!
新竹!!新年快樂!!
彰化!!新年快樂!!

今年的跨年跟大家一起在批踢踢跨年 XD

希望大家在新的一年有全新的開始

2020了!!!喔!!!!!!!!!!!(how how

每十推100P ~ 發到爆。
'''
    Content = Content.replace('\n', '\r\n')

    print(f'TargetPreTime {TargetPreTime}')
    print(f'Board {Board}')
    print(f'Title {Title}')
    print(f'Content {Content}')

    Ready = False
    LastTime = None
    try:
        while True:
            PTT_TIME = PTTBot.getTime()
            if PTT_TIME is None:
                print('PTT_TIME is None')
                continue

            if PTT_TIME == TargetPreTime:
                Ready = True
            elif Ready:
                # print(PTT_TIME)
                break
            if LastTime != PTT_TIME:
                LastTime = PTT_TIME
                print(PTT_TIME, end='\r')
            time.sleep(0.01)

        PTTBot.post(
            Board,
            Title,
            Content,
            2,
            3
        )
        print(PTT_TIME)
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass

    print('登出')
    PTTBot.logout()
