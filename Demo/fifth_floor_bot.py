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

    board = 'Test'

    ptt_bot = PTT.API()
    ptt_bot.login(id, pw, kick_other_login=True)

    last_index = 0

    push_content = [
        '冒險蓋 1 樓',
        '冒險蓋 2 樓',
        '冒險蓋 3 樓',
        '冒險蓋 4 樓',
        '就是愛搶五樓，送'
    ]

    while True:

        newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.BBS, board=board)
        print(f'{board} 板最新文章編號', newest_index)

        if last_index != newest_index and last_index != 0:

            for current_index in range(last_index + 1, newest_index + 1):
                post_info = ptt_bot.get_post(board, post_index=current_index)

                for push_index in range(len(post_info.push_list), 5):
                    ptt_bot.push(board, PTT.data_type.push_type.ARROW, push_content[push_index],
                                 post_index=current_index)

        last_index = newest_index

        try:
            time.sleep(2)
        except KeyboardInterrupt:
            break

    ptt_bot.logout()
