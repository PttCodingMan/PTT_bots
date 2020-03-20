import json
import sys
import traceback
import time
import datetime
from PyPtt import PTT


def get_password(password_file):
    try:
        with open(password_file) as AccountFile:
            account = json.load(AccountFile)
            ptt_id = account['ID']
            password = account['Password']
    except FileNotFoundError:
        print('Please note PTT ID and Password in Account.txt')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ptt_id, password


ptt_id, password = get_password('Account.txt')
while True:
    try:
        ptt_bot = PTT.API()
        try:
            ptt_bot.login(
                ptt_id,
                password,
                # kick_other_login=True
            )
        except PTT.exceptions.LoginError:
            ptt_bot.log('登入失敗')
            sys.exit()
        except PTT.exceptions.WrongIDorPassword:
            ptt_bot.log('帳號密碼錯誤')
            sys.exit()
        except PTT.exceptions.LoginTooOften:
            ptt_bot.log('請稍等一下再登入')
            sys.exit()

        if ptt_bot.unregistered_user:
            print('未註冊使用者')

            process_picks = -1
            if ptt_bot.process_picks != 0:
                process_picks = ptt_bot.process_picks
                print(f'註冊單處理順位 {ptt_bot.process_picks}')

            if process_picks == -1:
                ptt_bot.logout()
                continue

        if ptt_bot.registered_user:
            print('已註冊使用者!!!!!!!!!!!!!!!!!!')

        ptt2_bot = PTT.API(
            host=PTT.data_type.host_type.PTT2)
        try:
            ptt2_bot.login(
                ptt_id,
                password)
        except PTT.exceptions.LoginError:
            ptt_bot.log('登入失敗')
            sys.exit()
        except PTT.exceptions.WrongIDorPassword:
            ptt_bot.log('帳號密碼錯誤')
            sys.exit()
        except PTT.exceptions.LoginTooOften:
            ptt_bot.log('請稍等一下再登入')
            sys.exit()

        date = time.strftime("%m/%d", time.localtime())

        start_date = datetime.datetime(
            2020,
            3,
            16)

        today = datetime.datetime.today()

        delta = today - start_date
        delta = delta.days
        print(delta)

        content = f'{date} {process_picks} 尚須等待 {process_picks / delta} 天'
        print(content)

        ptt2_bot.push('CodingMan', PTT.data_type.push_type.ARROW, content, post_aid='1URkAo7l')

    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass

    ptt_bot.logout()
    ptt2_bot.logout()
    break
