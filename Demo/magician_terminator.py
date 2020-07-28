import sys
import time
import json
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
    id, pw = get_password('../Account.txt')

    board = 'AllTogether'

    ptt_bot = PTT.API()
    ptt_bot.login(id, pw, kick_other_login=True)

    last_index = 0

    while True:

        newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.BBS, board=board)
        print(f'{board} 板最新文章編號', newest_index)

        if last_index != newest_index and last_index != 0:

            for current_index in range(last_index + 1, newest_index + 1):
                # new post index here

                post_info = ptt_bot.get_post(board, post_index=current_index)

                author = post_info.author
                if '(' in author:
                    author = author[:author.find('(')].strip()

                if '徵男' in post_info.title:
                    ptt_bot.mail(author, '哈囉', '你好嗎?', 0)

        last_index = newest_index

        try:
            time.sleep(2)
        except KeyboardInterrupt:
            break

    ptt_bot.logout()
