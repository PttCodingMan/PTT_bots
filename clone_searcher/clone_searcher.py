import sys
import os
import time
import json
import threading
import string
import random
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


class Searcher:
    def __init__(self, id, pw, target):

        self.id = id
        self.pw = pw

        ptt_bot = PTT.API()
        ptt_bot.login(id, pw, kick_other_login=True)

        target_info = ptt_bot.get_user(target)

        self.target = target

        ptt_bot.logout()

        self.ip_list = set()
        self.ip_list.add(target_info.last_ip)

        self.possible_list = list()

        watch_thread = threading.Thread(target=self.watch)
        watch_thread.start()

        search_thread = threading.Thread(target=self.search)
        search_thread.start()

    def search(self):
        search_bot = PTT.API(log_level=PTT.log.level.SILENT)
        search_bot.login(self.id, self.pw)

        case_list = list(string.ascii_lowercase)
        random.shuffle(case_list)

        while True:

            for c in case_list:
                id_list = search_bot.search_user(c)
                random.shuffle(id_list)

                for current_user in id_list:
                    current_user_info = search_bot.get_user(current_user)
                    print('比對', current_user)
                    if current_user_info.last_ip in self.ip_list:
                        self.possible_list.append(current_user)

    def watch(self):
        watch_bot = PTT.API(log_level=PTT.log.level.SILENT)
        watch_bot.login(id, pw)

        refresh = True

        while True:

            if refresh:
                os.system('cls')

                print('目標: ', self.target)
                print('IP 清單: ', '\n'.join(self.ip_list))

                print('可能分身清單: ', ' '.join(self.possible_list))
                print('====================================')
                refresh = False

            target_info = watch_bot.get_user(self.target)
            if target_info.last_ip not in self.ip_list:
                print('find new ip', target_info.last_ip)
                self.ip_list.add(target_info.last_ip)

            time.sleep(3)
            if target_info.last_ip not in self.ip_list:
                refresh = True

        watch_bot.logout()


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('> python clone_search.py target_id')
        sys.exit()

    target = sys.argv[1]
    print(target)

    id, pw = get_password('../Account.txt')

    s = Searcher(id, pw, target)

