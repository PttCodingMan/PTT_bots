import sys
import json
import traceback
from PyPtt import PTT
from SingleLog.log import Logger


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


def crawl(board):
    global result
    result[board] = list()

    current_index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.BBS,
        board=board
    )
    logger.info('index', current_index)

    for i in range(20):
        post_info = ptt_bot.get_post(
            board,
            post_index=current_index - i
        )
        if post_info.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
            continue
        current_post = dict()

        current_post['author'] = post_info.author
        current_post['title'] = post_info.title
        current_post['date'] = post_info.date
        current_post['content'] = post_info.content

        result[board].append(current_post)


if __name__ == '__main__':
    logger = Logger('app', Logger.INFO)

    try:

        ptt_id, ptt_pw = get_password('Account.txt')
        ptt_bot = PTT.API()

        ptt_bot.login(ptt_id, ptt_pw)

        result = dict()

        crawl('ID_Multi')
        crawl('C_Chat')

        with open('PttApp/crawl.json', 'w', encoding='utf-8') as f:
            f.write(
                json.dumps(result, indent=4, ensure_ascii=False)
            )

    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass
    finally:
        ptt_bot.logout()
