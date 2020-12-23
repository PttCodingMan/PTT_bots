import sys
import json
import time
import traceback
from datetime import datetime
import tkinter
from tkinter import messagebox
root = tkinter.Tk()
root.withdraw()

from PyPtt import PTT

if __name__ == '__main__':
    try:
        with open('ptt_info.json', encoding='utf-8') as f:
            ptt_info = json.load(f)
    except FileNotFoundError:
        with open('ptt_info.json', 'w', encoding='utf-8') as f:
            sample = '''{
  "ptt_id": "你的 PTT ID",
  "ptt_pw": "你的 PTT Password",
  "post_aid": "簽到文章 AID"
}
'''
            f.write(sample)
            messagebox.showerror(title='25 周年簽到機器人', message='請修改 ptt_info.json 內的資訊')
            sys.exit()

    ptt_bot = PTT.API()
    try:
        ptt_bot.login(ptt_info['ptt_id'], ptt_info['ptt_pw'])
    except PTT.exceptions.WrongIDorPassword:
        messagebox.showerror(title='25 周年簽到機器人', message='帳號密碼錯誤，請確認 ptt_info.json 內的資訊')
        sys.exit()

    post_info = ptt_bot.get_post(
        'Ptt25sign',
        post_aid=ptt_info['post_aid']
    )
    if not post_info or not post_info.title or not post_info.author:
        messagebox.showerror(title='25 周年簽到機器人', message='驗證文章 AID 失敗，請確認 ptt_info.json 內的資訊')
        sys.exit()
    # print(post_info.title)
    # print(post_info.author)

    if ptt_info['ptt_id'] not in post_info.author:
        messagebox.showerror(title='25 周年簽到機器人', message='推文 ID 與簽到文 ID 不符，請確認 ptt_info.json 內的資訊')
        sys.exit()

    while True:

        today = datetime.now()

        sleep_time = datetime(
            today.year,
            today.month,
            today.day,
            23,
            57,
            0)
        delta = sleep_time - today
        sleep_sec = delta.seconds
        print('預計', sleep_sec + 180, '秒後推文')
        print(int(sleep_sec / 3600), '小時又', int(((sleep_sec + 180) % 3600) / 60), '分鐘')

        time.sleep(sleep_sec)

        # 預定 PO 文時間的 "前一分鐘"
        target_pre_time = '23:59'

        # 文章內文
        content = '簽到'

        ready = False
        last_time = None

        ptt_bot = PTT.API(
            # LogLevel=PTT.LogLevel.TRACE
        )

        try:

            ptt_bot.login(ptt_info['ptt_id'], ptt_info['ptt_pw'])

            while True:

                slow_detect_time = 55
                start_time = end_time = time.time()
                next_min = False

                last_time = current_time = ptt_bot.get_time()
                while end_time - start_time < slow_detect_time:
                    time.sleep(1)
                    end_time = time.time()
                    current_time = ptt_bot.get_time()

                    if last_time != current_time:
                        next_min = True
                        break

                    last_time = current_time
                    # print(current_time, end='\r')
                    ptt_bot.log(current_time)
                    if target_pre_time == current_time:
                        ready = True

                if next_min:
                    continue

                if ready:
                    print('最後準備')
                    while last_time == current_time:
                        current_time = ptt_bot.get_time()
                    break

                # 批踢踢的一分鐘過了

            ptt_bot.push(
                'Ptt25sign',
                PTT.data_type.push_type.ARROW,
                content,
                post_aid=ptt_info['post_aid']
            )

        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        except KeyboardInterrupt:
            pass

        print('登出                 ')
        ptt_bot.logout()
