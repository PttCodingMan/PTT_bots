

import sys
import os
import time
import json
import random
import traceback
import PTTLibrary
import threading

from PTTLibrary import PTT


def getPW():
    try:
        with open('Account3.txt') as AccountFile:
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

        ptt_bot = PTT.Library()
        try:
            ptt_bot.login(
                ID,
                Password
            )
        except PTT.Exceptions.LoginError:
            ptt_bot.log('登入失敗')
            sys.exit()

        current_board = 'QQBoard'

        NewIndex = ptt_bot.getNewestIndex(
            PTT.IndexType.BBS,
            current_board
        )
        print(f'{current_board} 最新文章編號 {NewIndex}')

        find = False

        for index in range(1, NewIndex + 1):

            print(f'文章編號 {NewIndex - index}')

            Post = ptt_bot.getPost(
                current_board,
                PostIndex=NewIndex - index
            )

            Pushlist = Post.getPushList()

            if Pushlist is None:
                continue
            for push in Pushlist:
                # print(f'Author [{push.getAuthor()}]')
                if 'QQID' in push.getAuthor().lower():
                    print('!!!!!!!!!!!!!!!!!!!!!!!')
                    find = True
                    break

            if find:
                break

    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)

    ptt_bot.logout()
