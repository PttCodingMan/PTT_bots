
import sys
import os
import time
import json
import random
import traceback
import PTTLibrary
import threading

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from PTTLibrary import PTT

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
    os.system('cls')

    ID, Password = getPW()
    PTTBot = PTT.Library()

    try:
        try:
            PTTBot.login(
                ID,
                Password,
            )
            pass
        except PTT.Exceptions.LoginError:
            PTTBot.log('登入失敗')
            sys.exit()

        lastcontent = None
        while True:

            while True:
                # 取得中選會網頁資料

                ticke_1 = 1
                ticke_2 = 2
                ticke_3 = 3

                try:
                    response = requests.get(
                        'https://www.cec.gov.tw/pc/zh_TW/P1/n00000000000000000.html',
                        verify=False
                    )
                except requests.exceptions.ConnectionError:
                    print('取得 ERP 資料失敗')

                Source = response.text
                # print(Source)

                Sourcelines = Source.split('\n')
                Sourcelines = [x.strip() for x in Sourcelines if x.strip().startswith('<td') and 'tdAlignRight' in x]
                for i, line in enumerate(Sourcelines):
                    # print(f'line [{line}]')
                    if i == 0:
                        line = line[line.find('>') + 1:]
                        line = line[:line.find('<')].replace(',', '')
                        ticke_1 = int(line)
                    if i == 2:
                        line = line[line.find('>') + 1:]
                        line = line[:line.find('<')].replace(',', '')
                        ticke_2 = int(line)
                    if i == 4:
                        line = line[line.find('>') + 1:]
                        line = line[:line.find('<')].replace(',', '')
                        ticke_3 = int(line)

                # 推文格式
                # 中選會 2號 1001111 3號 8001111

                Content = f'中選會 韓 {ticke_2} 蔡 {ticke_3}'

                print(Content)
                if lastcontent != Content:
                    lastcontent = Content
                    break
                time.sleep(3)
                PTTBot.getTime()

            PTTBot.push('Gossiping', PTT.PushType.Arrow,
                        Content, PostIndex=786734)


    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass

    PTTBot.logout()
