import threading
import json
from PyPtt import PTT


class Crawler:
    def __init__(self, account_file_name, board, start_index, end_index, number_threads: int = 5):
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
            # print(index)
            post_info = ptt_bot.get_post(board, post_index=index)

            # Do anything you want here!!!

        ptt_bot.logout()


if __name__ == '__main__':
    board = 'Gossiping'
    test_range = 100

    end_index = 779306

    start_index = end_index - test_range + 1

    import time

    start_time = time.time()
    Crawler('account_list.txt', board, start_index, end_index)
    end_time = time.time()

    total_time = int(end_time - start_time)

    print(f'爬行 {board} 共 {test_range} 篇文章 共耗費時間 %.2f 秒' % total_time)
