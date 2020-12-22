import json
import time
from datetime import datetime

from PyPtt import PTT

if __name__ == '__main__':
    with open('ptt_info.json') as f:
        ptt_info = json.load(f)
    # print(ptt_info)

    while True:

        today = datetime.now()

        sleep_time = datetime(
            today.year,
            today.month,
            today.day,
            23,
            58,
            0)
        delta = sleep_time - today
        sleep_sec = delta.seconds
        print('預計', sleep_sec + 120, '秒後推文')
        print(int(sleep_sec / 3600), '小時又', int(((sleep_sec + 120) % 3600) / 60), '分鐘')

        time.sleep(sleep_sec)

        # 預定 PO 文時間的 "前一分鐘"
        target_pre_time = '23:59'

        # 文章內文
        content = '''
        零秒 PO文新版演算法
        '''
        content = content.replace('\n', '\r\n')

        print(f'TargetPreTime {target_pre_time}')
        print(f'Board {current_board}')
        print(f'Title {title}')
        print(f'Content {content}')

        ready = False
        last_time = None

        ptt_bot = PTT.API(
            # LogLevel=PTT.LogLevel.TRACE
        )

        try:
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

            ptt_bot.post(
                current_board,
                title,
                content,
                2,
                3)

        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        except KeyboardInterrupt:
            pass

        print('登出                 ')
        ptt_bot.logout()




    # print()

    # ptt_bot = PTT.API(
    #     # LogLevel=PTT.LogLevel.TRACE
    # )
    #
    # ptt_bot.login(ptt_info['ptt_id'], ptt_info['ptt_pw'])
    # ptt_bot.push('Ptt25sign', PTT.data_type.push_type.PUSH, content, post_index=test_index)