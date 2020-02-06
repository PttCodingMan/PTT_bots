
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
    ptt_bot = PTT.Library(
        # LogLevel=PTT.LogLevel.TRACE
    )

    ID, Password = getPW()

    try:
        ptt_bot.login(
            ID,
            Password,
            # KickOtherLogin=True
        )
    except PTT.Exceptions.LoginError:
        ptt_bot.log('登入失敗')
        sys.exit()

    TargetPreTime = '22:01'

    current_board = 'Test'
    Title = '零秒PO文新版演算法測試'
    Content = '''
零秒 PO文新版演算法
'''
    Content = Content.replace('\n', '\r\n')

    print(f'TargetPreTime {TargetPreTime}')
    print(f'Board {current_board}')
    print(f'Title {Title}')
    print(f'Content {Content}')

    Ready = False
    LastTime = None

    try:
        while True:

            SlowDetectTime = 55
            StartTime = EndTime = time.time()
            NextMin = False

            LastTime = CurrentTime = ptt_bot.getTime()
            while EndTime - StartTime < SlowDetectTime:
                time.sleep(1)
                EndTime = time.time()
                CurrentTime = ptt_bot.getTime()

                if LastTime != CurrentTime:
                    NextMin = True
                    break

                LastTime = CurrentTime
                # print(CurrentTime, end='\r')
                ptt_bot.log(CurrentTime)
                if TargetPreTime == CurrentTime:
                    Ready = True

            if NextMin:
                continue

            if Ready:
                print('最後準備')
                while LastTime == CurrentTime:
                    CurrentTime = ptt_bot.getTime()
                break
            else:
                while LastTime == CurrentTime:
                    time.sleep(1)
                    CurrentTime = ptt_bot.getTime()
                    ptt_bot.log(f'slow area {CurrentTime}')
                    # print(f'slow area {CurrentTime}', end='\r')

            # 批踢踢的一分鐘過了

        ptt_bot.post(
            current_board,
            Title,
            Content,
            2,
            3
        )

    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass

    print('登出                 ')
    ptt_bot.logout()
