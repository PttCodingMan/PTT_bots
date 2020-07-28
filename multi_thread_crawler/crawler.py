import threading
import json
from PyPtt import PTT
import os


class Crawler:
    def __init__(self, account_file_name, board, start_index, end_index, number_threads: int = 6):
        with open(account_file_name) as f:
            account = json.load(f)

        if number_threads < 1 or len(account) * 3 < number_threads:
            raise ValueError()

        if 0 < number_threads <= len(account):
            account_use = 1
        else:
            account_use = 3

        # print(len(self.account))
        # print(account_use)

        # print(start_index)
        # print(end_index)

        total_index = end_index - start_index + 1
        basic_index = int(total_index / number_threads)
        # print(total_index)
        # print(basic_index)

        start = start_index
        id_count = dict()
        id_index = 0

        thread_list = list()

        for thread_index in range(number_threads):
            # print('====')
            end = start + basic_index - 1
            if thread_index < (total_index % number_threads):
                end += 1

            if list(account.keys())[id_index] not in id_count:
                id_count[list(account.keys())[id_index]] = 0
            if id_count[list(account.keys())[id_index]] >= account_use:
                id_index += 1
                if list(account.keys())[id_index] not in id_count:
                    id_count[list(account.keys())[id_index]] = 0

            id_count[list(account.keys())[id_index]] += 1

            id = list(account.keys())[id_index]
            pw = account[id]

            # print(start, end)

            t = threading.Thread(target=self.crawl_worker, args=(id, pw, board, start, end))
            t.start()

            thread_list.append(t)

            start = end + 1

        for t in thread_list:
            t.join()

    def crawl_worker(self, id, pw, board, start_index, end_index):
        ptt_bot = PTT.API()
        ptt_bot.login(id, pw)

        for index in range(start_index, end_index + 1):
            try:
                post_info = ptt_bot.get_post(board, post_index=index)
            except:
                print('get_post error', index)
                continue
            if post_info is None:
                continue

            if post_info.date is None:
                print('aid', post_info.aid)
                print('內文', post_info.content)
                print('===========')
                continue

            # print(post_info.title)
            try:
                date = post_info.date.split(' ')
                date.pop(0)
                date.insert(0, date[-1])
                date.pop()
                date = [x for x in date if len(x) != 0]
                if len(date[2]) == 1:
                    date[2] = '0' + date[2]
                file_name = '_'.join(date).replace(':', '.') + '.json'

                if len(file_name) != 25:
                    print('aid', post_info.aid)
                    print('file name error', file_name)
                    print('date error', post_info.date)
                    print('===========')

                    continue
            except:
                print('aid', post_info.aid)
                print('date error', post_info.date)
                print('===========')
                continue

            data = dict()
            data['aid'] = post_info.aid
            data['author'] = post_info.author
            data['title'] = post_info.title
            data['date'] = post_info.date
            data['location'] = post_info.location
            data['content'] = post_info.content
            data['ip'] = post_info.ip

            push_list = list()
            for push in post_info.push_list:
                current_push = dict()
                current_push['author'] = push.author
                current_push['content'] = push.content
                current_push['time'] = push.time
                push_list.append(current_push)

            data['push_list'] = push_list

            if os.path.isfile(f'LAW/{file_name}'):
                continue
            with open(f'LAW/{file_name}', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            # print(file_name)
            # Do anything you want here!!!

        ptt_bot.logout()


if __name__ == '__main__':
    board = 'LAW'
    end_index = 32598

    start_index = 1

    import time

    start_time = time.time()
    Crawler('account_list.txt', board, start_index, end_index)
    end_time = time.time()

    total_time = int(end_time - start_time)

    print(f'爬行 {board} 共耗費時間 %.2f 秒' % total_time)
