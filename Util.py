
import sys
import os
from PyPtt import PTT
from datetime import date, timedelta, datetime

ptt_bot = None
current_board = 'ALLPOST'
post_search_type = PTT.data_type.post_search_type.KEYWORD
post_search = '(Wanted)'


def get_date(time_del, ptt_sytle=True):
    pass_day = date.today() - timedelta(time_del)

    pass_date = pass_day.strftime("%m/%d")
    # print('>' + pass_date + '<')
    if ptt_sytle and pass_date.startswith('0'):
        pass_date = pass_date[1:]

    return pass_date


def get_target(date0, date1):

    today = int(datetime.today().strftime('%m%d'))

    if int(date0) > today:
        date0 = '0' + date0
    else:
        date0 = '1' + date0

    if int(date1) > today:
        date1 = '0' + date1
    else:
        date1 = '1' + date1

    return int(date0 + date1)


HistoryList = dict()


def find_current_date_first(biggest_target, newest_index, day_ago, show=False, oldest_index=1):

    global ptt_bot
    global current_board

    # global HistoryList

    # if str(DayAgo) in HistoryList:
    #     return HistoryList[str(DayAgo)]

    current_date_0 = get_date(
        day_ago + 1, ptt_sytle=False).replace('/', '').strip()
    current_date_1 = get_date(day_ago, ptt_sytle=False).replace('/', '').strip()
    finish_target = get_target(current_date_0, current_date_1)

    if show:
        print(f'current_date_0 {current_date_0}')
        print(f'current_date_1 {current_date_1}')
        print(f'finish_target {finish_target}')

    start_index = oldest_index
    end_index = newest_index

    if show:
        print(f'start_index {start_index}')
        print(f'end_index {end_index}')

    current_index = int((start_index + end_index) / 2)
    retry_index = 0

    while True:
        if show:
            ptt_bot.log('嘗試: ' + str(current_index))
            print('Board:', current_board)
            print('current_index:', current_index)
            print('PostSearchType:', post_search_type)
            print('PostSearch:', post_search)

        post_1 = ptt_bot.get_post(
            current_board,
            post_index=current_index,
            search_type=post_search_type,
            search_condition=post_search,
            query=True
        )

        if post_1.list_date is None:
            current_index = start_index + retry_index
            retry_index += 1
            continue

        post_0 = None
        retry_index = 0
        for i in range(1, 40):

            if current_index - i <= 0:
                break

            post_0 = ptt_bot.get_post(
                current_board,
                post_index=(current_index - i),
                search_type=post_search_type,
                search_condition=post_search,
                query=True
            )

            if post_0 is None:
                continue
            elif post_0.list_date is None:
                continue

            if show:
                ptt_bot.log('找到上一篇: ' + str(current_index - i))
            break

        if post_0 is None:
            current_date_0 = '0000'
        else:
            current_date_0 = post_0.list_date.replace('/', '').strip()

        if len(current_date_0) < 4:
            current_date_0 = '0' + current_date_0
        current_date_1 = post_1.list_date.replace('/', '').strip()
        if len(current_date_1) < 4:
            current_date_1 = '0' + current_date_1
        current_target = get_target(current_date_0, current_date_1)

        if show:
            print('current_date_0: ' + current_date_0)
            print('current_date_1: ' + current_date_1)
            print('current_target: ' + str(current_target))
            print('finish_target: ' + str(finish_target))
            print(start_index)
            print(end_index)

        if current_target == finish_target:
            HistoryList[str(day_ago)] = current_index
            return current_index

        if current_target > finish_target:
            end_index = current_index - 1
        elif current_target < finish_target:
            start_index = current_index + 1
        current_index = int((start_index + end_index) / 2)


def find_post_range(DayAgo, show=False):
    global ptt_bot
    global current_board
    global post_search_type
    global post_search

    if show:
        print('Board:', current_board)
        print('SearchType:', post_search_type)
        print('Search:', post_search)

    if post_search is not None:
        newest_index = ptt_bot.get_newest_index(
            PTT.data_type.index_type.BBS,
            board=current_board,
            search_type=post_search_type,
            search_condition=post_search,
        )
    else:
        newest_index = ptt_bot.getNewestIndex(
            PTT.data_type.index_type.BBS,
            board=current_board,
        )

    if newest_index == -1:
        ptt_bot.log('取得 ' + current_board + ' 板最新文章編號失敗')
        sys.exit()
    ptt_bot.log('取得 ' + current_board + ' 板最新文章編號: ' + str(newest_index))

    if post_search is not None:
        post_info = ptt_bot.get_post(
            current_board,
            post_index=newest_index,
            search_type=post_search_type,
            search_condition=post_search,
            query=True
        )
    else:
        post_info = ptt_bot.getPost(
            current_board,
            post_index=newest_index,
            query=True
        )

    current_date_0 = post_info.list_date.replace('/', '').strip()
    if len(current_date_0) < 4:
        current_date_0 = '0' + current_date_0
    current_date_1 = current_date_0
    if len(current_date_1) < 4:
        current_date_1 = '0' + current_date_1

    biggest_target = get_target(current_date_0, current_date_1)
    if show:
        print(f'biggest_target {biggest_target}')

    Start = find_current_date_first(
        biggest_target, newest_index, DayAgo, show=False)

    if show:
        print(f'Start {Start}')

    if DayAgo > 0:
        end = find_current_date_first(
            biggest_target, newest_index, DayAgo - 1, show=False, oldest_index=Start) - 1
    elif DayAgo == 0:
        end = newest_index

    if show:
        print('Result', Start, end)

    return Start, end
