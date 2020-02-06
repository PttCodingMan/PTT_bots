import sys
import json

from PTTLibrary import PTT


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


ID, Password = getPW()

try:
    # Loginout()
    # ThreadingTest()

    ptt_bot = PTT.Library(
        # LogLevel=PTT.LogLevel.TRACE,
        # LogLevel=PTT.LogLevel.DEBUG,
        # Host=PTT.Host.PTT2
    )
    try:
        ptt_bot.login(
            ID,
            Password,
            # KickOtherLogin=True
        )
        pass
    except PTT.Exceptions.LoginError:
        ptt_bot.log('登入失敗')
        sys.exit()

    BoardList = ptt_bot.getBoardList()
    # print(' '.join(BoardList))
    print(f'總共有 {len(BoardList)} 個板名')
    print(f'總共有 {len(set(BoardList))} 個不重複板名')

    ErrorList = []

    result = dict()

    # TempStr = ''
    for board in BoardList:
        try:
            BoardInfo = ptt_bot.getBoardInfo(board)
        except PTT.Exceptions.NoSuchBoard:
            print(f'No Such Board {board}')
            ErrorList.append(board)
            result[board] = 'Unknow'
            continue

        current = dict()
        # current['Name'] = board
        # current['Nuser'] = str(BoardInfo.getOnlineUser())

        # Class = BoardInfo.getChineseDes()
        # Class = Class[:Class.find('◎')].strip()
        # current['Class'] = Class

        # Title = BoardInfo.getChineseDes()
        # Title = Title[Title.find('◎') + 1:].strip()
        # current['Title'] = Title

        # current['Href'] = f'/bbs/{board}/index.html'
        # current['MaxSize'] = 0

        current['線上人數'] = BoardInfo.getOnlineUser()
        current['中文敘述'] = BoardInfo.getChineseDes()
        current['板主'] = BoardInfo.getModerators()
        current['公開狀態'] = BoardInfo.isOpen()
        current['隱板時是否可進入十大排行榜'] = BoardInfo.canIntoTopTenWhenHide()
        current['是否開放非看板會員發文'] = BoardInfo.canNonBoardMembersPost()
        current['是否開放回應文章'] = BoardInfo.canReplyPost()
        current['是否開放自刪文章'] = BoardInfo.canSelfDelPost()
        current['是否開放推薦文章'] = BoardInfo.canPushPost()
        current['是否開放噓文'] = BoardInfo.canBooPost()
        current['是否可以快速連推文章'] = BoardInfo.canFastPush()
        current['推文最低間隔時間'] = BoardInfo.getMinInterval()
        current['推文時是否記錄來源 IP'] = BoardInfo.isPushRecordIP()
        current['推文時是否對齊開頭'] = BoardInfo.isPushAligned()
        current['板主是否可刪除部份違規文字'] = BoardInfo.canModeratorCanDelIllegalContent()
        current['轉錄文章是否自動記錄且是否需要發文權限'] = BoardInfo.isTranPostAutoRecordedAndRequirePostPermissions()
        current['冷靜模式'] = BoardInfo.isCoolMode()
        current['需要滿十八歲才可進入'] = BoardInfo.isRequire18()
        current['發文與推文限制登入次數需多少次以上'] = BoardInfo.getRequireLoginTime()
        current['發文與推文限制退文篇數多少篇以下'] = BoardInfo.getRequireIllegalPost()

        result[board] = current

    print(ErrorList)

    with open('BoardList.json', 'w', encoding='utf8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

except Exception as e:
    traceback.print_tb(e.__traceback__)
    print(e)
except KeyboardInterrupt:
    pass

ptt_bot.logout()
