import datetime
import os
import sys
import time
import traceback

from PyPtt import PTT

ptt_id, ptt_pw = 'Your PTT ID', 'Your PTT PW'
release = False

if __name__ == '__main__':
    time_bot = PTT.API()

    try:
        time_bot.login(
            ptt_id,
            ptt_pw,
            kick_other_login=True
        )
        time_bot.logout()
    except PTT.exceptions.LoginError:
        time_bot.log('登入失敗 ' + ptt_id)
        sys.exit()

    time.sleep(10)

    time_bot = PTT.API()
    post_bot = PTT.API()

    for _ in range(5):
        try:
            time_bot.login(ptt_id, ptt_pw)
            time.sleep(5)
            post_bot.login(ptt_id, ptt_pw)
            break
        except PTT.exceptions.LoginError:
            time_bot.log('登入失敗 ' + ptt_id)
        except PTT.exceptions.LoginTooOften:
            time_bot.log('登入太頻繁')
        time.sleep(5)

    content = PTT.command.Ctrl_Y * 10 + f'''不好意思，搶到首PO

想請問一下有 2023 首PO的八卦嗎?

--

Post by https://pyptt.cc/
'''

    if release:
        target_pre_time = '23:59'
        current_board = 'Gossiping'

        title = '請問有 2023 首PO的八卦嗎?'
        post_type = 3

    else:
        target_pre_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%H:%M')
        current_board = 'Test'

        title = '準點 PO 文測試'
        post_type = 1

    content = content.replace('\n', '\r\n')

    print('Python 版本: ' + sys.version)
    print(f'目標前一分鐘 {target_pre_time}')
    print(f'目標看板 {current_board}')
    print(f'文章分類 {post_type}')
    print(f'文章標題 {title}')
    print(f'文章內文 {content}')

    ready = False
    last_time = None

    try:
        while True:

            slow_detect_time = 50
            start_time = end_time = time.time()
            next_min = False

            last_time = current_time = time_bot.get_time()
            while end_time - start_time < slow_detect_time:
                time.sleep(2)
                end_time = time.time()
                current_time = time_bot.get_time()
                post_bot.get_time()

                if last_time != current_time:
                    next_min = True
                    break

                last_time = current_time
                # print(current_time, end='\r')
                time_bot.log(current_time)
                if target_pre_time == current_time:
                    ready = True

            if next_min:
                continue

            if ready:

                post_bot.fast_post_step0(
                    current_board,
                    title,
                    content,
                    post_type)
                time_bot.log('最後準備')
                while last_time == current_time:
                    current_time = time_bot.get_time()

                post_bot.fast_post_step1(0)
                # print(time.time())
                break

    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass
    finally:
        time_bot.logout()
        post_bot.logout()

    print('登出                 ')
