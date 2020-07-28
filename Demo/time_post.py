import sys
import os
import time
import json
import traceback

from PyPtt import PTT


def get_password(password_file):
    try:
        with open(password_file) as AccountFile:
            account = json.load(AccountFile)
            ptt_id = account['ID']
            password = account['Password']
    except FileNotFoundError:
        print(f'Please note PTT ID and Password in {password_file}')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ptt_id, password


if __name__ == '__main__':
    os.system('cls')
    ptt_bot = PTT.API()

    ID, Password = get_password('../Account2.txt')

    try:
        ptt_bot.login(
            ID,
            Password,
            # KickOtherLogin=True
        )
    except PTT.exceptions.LoginError:
        ptt_bot.log('登入失敗')
        sys.exit()

    # 預定 PO 文時間的 "前一分鐘"
    target_pre_time = '11:21'

    # PO 文看板
    current_board = 'Test'
    # 文章標題
    title = '零秒PO文新版演算法測試'
    # 文章內文
    content = '''
零秒 PO文新版演算法
'''
    content = content.replace('\n', '\r\n')

    print(f'TargetPreTime {target_pre_time}')
    print(f'Board {current_board}')
    print(f'Title {title}')
    print(f'Content {content}')

    ready = False
    last_time = None

    try:
        while True:

            slow_detect_time = 55
            start_time = end_time = time.time()
            next_min = False

            last_time = current_time = ptt_bot.get_time()
            while end_time - start_time < slow_detect_time:
                time.sleep(1)
                end_time = time.time()
                current_time = ptt_bot.get_time()

                if last_time != current_time:
                    next_min = True
                    break

                last_time = current_time
                # print(current_time, end='\r')
                ptt_bot.log(current_time)
                if target_pre_time == current_time:
                    ready = True

            if next_min:
                continue

            if ready:
                print('最後準備')
                while last_time == current_time:
                    current_time = ptt_bot.get_time()
                break

            # 批踢踢的一分鐘過了

        ptt_bot.post(
            current_board,
            title,
            content,
            2,
            3)

    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass

    print('登出                 ')
    ptt_bot.logout()
