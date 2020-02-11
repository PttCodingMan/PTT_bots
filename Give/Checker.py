
import sys
import os
import time
import json
import getpass
import codecs
import traceback
import math
from datetime import date, timedelta
# from time import gmtime, strftime

from PTTLibrary import PTT
# from .. import Util

if __name__ == '__main__':

    try:
        with open('../Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')

    ptt_bot = PTT.Library()
    ptt_bot.login(ID, Password, KickOtherLogin=True)

    current_board = 'give'

    NewestIndex = ptt_bot.getNewestIndex(
        PTT.IndexType.BBS,
        current_board,
    )

    print(f'{current_board} 板最新編號 {NewestIndex}')

    SuspectList = []
    CheckList = [
        '過期',
        '門號',
        '市話',
        '寬頻',
        '網路',
        'sim',
        '帳號',
        '槍',
        '砲',
        '彈',
        '煙火',
        '藥',
        '隱形眼鏡',
        '隱眼',
        '菸',
        '煙',
        '酒',
        'https://www.ruten.com.tw/',
        'https://shopping.pchome.com.tw/',
        'https://shopee.tw/',
        'momo',
    ]
    for index in range(0, NewestIndex - 1):

        CurrentIndex = NewestIndex - index

        # print(f'讀取 {CurrentIndex}')

        Post = ptt_bot.getPost(
            current_board,
            PostIndex=CurrentIndex,
        )

        if Post.getDeleteStatus() != PTT.post_delete_status.NotDeleted:
            continue

        if '[公告]' in Post.getTitle():
            print('搜尋完畢')
            break

        Suspect = False

        Content = Post.getOriginPost().lower()
        if '--------------------' in Content:
            Content = Content[
                Content.find('--------------------'):
            ]

        if '食品及美妝品請加上到期日' in Content:
            Content = Content.replace('食品及美妝品請加上到期日', '')

        Reason = None
        for check in CheckList:

            if check in Content:
                Suspect = True
                if Reason is None:
                    Reason = f'疑似贈送 [{check}]'
                else:
                    Reason = f'{Reason}\n疑似贈送 [{check}]'

        if Suspect:
            print(Post.getOriginPost())
            print(Reason)
            print('=' * 50)
            print('=' * 50)
            print('=' * 50)