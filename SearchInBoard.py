

import sys
import os
import time
import json
import random
import traceback
import threading

from PyPtt import PTT


def getPW():
    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        print('Please note PTT ID and Password in Account.txt')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ID, Password


if __name__ == '__main__':

    ID, Password = getPW()

    try:

        ptt_bot = PTT.API()
        try:
            ptt_bot.login(
                ID,
                Password
            )
        except PTT.Exceptions.LoginError:
            ptt_bot.log('登入失敗')
            sys.exit()

        current_board = 'QQBoard'

        newest_index = ptt_bot.get_newest_index(
            PTT.data_type.index_type.BBS,
            current_board,
        )
        print(f'{current_board} 最新文章編號 {newest_index}')

        find = False

        for index in range(0, newest_index + 1):

            if index % 100 == 0:
                print(f'文章編號 {newest_index - index}')

            post_info = ptt_bot.get_post(
                current_board,
                post_index=newest_index - index)

            if post_info.origin_post is None:
                continue

            if 'QQID' in post_info.origin_post.lower():
                print('!!!!!!!!!!!!')
                print(post_info.aid)
                print('!!!!!!!!!!!!')
                break



    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)

    ptt_bot.logout()
