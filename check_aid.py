import json
import sys
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

    with open('check.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    current_board = data['BoardInfo']['Name']
    # print(current_board)

    ptt_id, password = get_password('Account.txt')
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

        for check_post in data['PostList']:

            # 過濾掉奇怪的字元
            current_title = check_post['Title']
            current_title = current_title[current_title.rfind(']') + 1:].strip()

            current_author = check_post['Author']

            current_aid = check_post['AID']

            # print(current_aid)

            ptt_post = ptt_bot.get_post(
                current_board,
                post_aid=current_aid,
                query=True)

            if current_title not in ptt_post.title:
                print(f'資料標題 [{current_title}]')
                print(f'批踢踢標題 [{ptt_post.title}]')
                print('標題比對失敗')
                continue

            if current_author not in ptt_post.author:
                print(f'資料作者 [{current_author}]')
                print(f'批踢踢作者 [{ptt_post.author}]')
                print('作者比對失敗')
                continue

            print('比對成功')

    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass

    ptt_bot.logout()
