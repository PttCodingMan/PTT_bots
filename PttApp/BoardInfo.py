

BoardList = PTTBot.getBoardList()
# print(' '.join(BoardList))
print(f'總共有 {len(BoardList)} 個板名')
print(f'總共有 {len(set(BoardList))} 個不重複板名')

ErrorList = []

result = dict()

# TempStr = ''
for board in BoardList:
    try:
        BoardInfo = PTTBot.getBoardInfo(board)
    except PTT.Exceptions.NoSuchBoard:
        print(f'No Such Board {board}')
        ErrorList.append(board)
        continue

    current = dict()
    current['Name'] = board
    current['Nuser'] = str(BoardInfo.getOnlineUser())

    Class = BoardInfo.getChineseDes()
    Class = Class[:Class.find('◎')].strip()
    current['Class'] = Class

    Title = BoardInfo.getChineseDes()
    Title = Title[Title.find('◎') + 1:].strip()
    current['Title'] = Title

    current['Href'] = f'/bbs/{board}/index.html'
    current['MaxSize'] = 0

    result[board] = current

print(ErrorList)

with open('BoardList.json', 'w', encoding='utf8') as f:
    json.dump(result, f, indent=4, ensure_ascii=False)