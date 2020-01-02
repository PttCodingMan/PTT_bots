
import sys
import os
from PTTLibrary import PTT
from datetime import date, timedelta, datetime

PTTBot = None
Board = 'ALLPOST'
PostSearchType = PTT.PostSearchType.Keyword
PostSearch = '(Wanted)'
Moderators = ['gogin']


def getDate(TimeDel, PTTSytle=True):
    PassDay = date.today() - timedelta(TimeDel)

    PassDate = PassDay.strftime("%m/%d")
    # print('>' + PassDate + '<')
    if PTTSytle and PassDate.startswith('0'):
        PassDate = PassDate[1:]

    return PassDate


def getTarget(Date0, Date1):

    Today = int(datetime.today().strftime('%m%d'))

    if int(Date0) > Today:
        Date0 = '0' + Date0
    else:
        Date0 = '1' + Date0

    if int(Date1) > Today:
        Date1 = '0' + Date1
    else:
        Date1 = '1' + Date1

    return int(Date0 + Date1)


HistoryList = dict()


def findCurrentDateFirst(BiggestTarget, NewestIndex, DayAgo, show=False, OldestIndex=1):

    global PTTBot
    global Board
    global Moderators

    # global HistoryList

    # if str(DayAgo) in HistoryList:
    #     return HistoryList[str(DayAgo)]

    CurrentDate_0 = getDate(
        DayAgo + 1, PTTSytle=False).replace('/', '').strip()
    CurrentDate_1 = getDate(DayAgo, PTTSytle=False).replace('/', '').strip()
    FinishTarget = getTarget(CurrentDate_0, CurrentDate_1)

    if show:
        print(f'CurrentDate_0 {CurrentDate_0}')
        print(f'CurrentDate_1 {CurrentDate_1}')
        print(f'FinishTarget {FinishTarget}')

    StartIndex = OldestIndex
    EndIndex = NewestIndex

    if show:
        print(f'StartIndex {StartIndex}')
        print(f'EndIndex {EndIndex}')

    CurrentIndex = int((StartIndex + EndIndex) / 2)
    RetryIndex = 0

    while True:
        if show:
            PTTBot.log('嘗試: ' + str(CurrentIndex))
            print('Board:', Board)
            print('CurrentIndex:', CurrentIndex)
            print('PostSearchType:', PostSearchType)
            print('PostSearch:', PostSearch)

        Post_1 = PTTBot.getPost(
            Board,
            PostIndex=CurrentIndex,
            SearchType=PostSearchType,
            SearchCondition=PostSearch,
            Query=True
        )

        if Post_1.getListDate() is None:
            CurrentIndex = StartIndex + RetryIndex
            RetryIndex += 1
            continue

        Post_0 = None
        RetryIndex = 0
        for i in range(1, 40):

            if CurrentIndex - i <= 0:
                break

            Post_0 = PTTBot.getPost(
                Board,
                PostIndex=(CurrentIndex - i),
                SearchType=PostSearchType,
                SearchCondition=PostSearch,
                Query=True
            )

            if Post_0 is None:
                continue
            elif Post_0.getListDate() is None:
                continue

            if show:
                PTTBot.log('找到上一篇: ' + str(CurrentIndex - i))
            break

        if Post_0 is None:
            CurrentDate_0 = '0000'
        else:
            CurrentDate_0 = Post_0.getListDate().replace('/', '').strip()

        if len(CurrentDate_0) < 4:
            CurrentDate_0 = '0' + CurrentDate_0
        CurrentDate_1 = Post_1.getListDate().replace('/', '').strip()
        if len(CurrentDate_1) < 4:
            CurrentDate_1 = '0' + CurrentDate_1
        CurrentTarget = getTarget(CurrentDate_0, CurrentDate_1)

        if show:
            print('CurrentDate_0: ' + CurrentDate_0)
            print('CurrentDate_1: ' + CurrentDate_1)
            print('CurrentTarget: ' + str(CurrentTarget))
            print('FinishTarget: ' + str(FinishTarget))
            print(StartIndex)
            print(EndIndex)

        if CurrentTarget == FinishTarget:
            HistoryList[str(DayAgo)] = CurrentIndex
            return CurrentIndex

        if CurrentTarget > FinishTarget:
            EndIndex = CurrentIndex - 1
        elif CurrentTarget < FinishTarget:
            StartIndex = CurrentIndex + 1
        CurrentIndex = int((StartIndex + EndIndex) / 2)


def findPostRrange(DayAgo, show=False):
    global PTTBot
    global Board
    global Moderators
    global PostSearchType
    global PostSearch

    if show:
        print('Board:', Board)
        print('SearchType:', PostSearchType)
        print('Search:', PostSearch)

    if PostSearch is not None:
        NewestIndex = PTTBot.getNewestIndex(
            PTT.IndexType.BBS,
            Board=Board,
            SearchType=PostSearchType,
            SearchCondition=PostSearch,
        )
    else:
        NewestIndex = PTTBot.getNewestIndex(
            PTT.IndexType.BBS,
            Board=Board,
        )

    if NewestIndex == -1:
        PTTBot.log('取得 ' + Board + ' 板最新文章編號失敗')
        sys.exit()
    PTTBot.log('取得 ' + Board + ' 板最新文章編號: ' + str(NewestIndex))

    if PostSearch is not None:
        Post = PTTBot.getPost(
            Board,
            PostIndex=NewestIndex,
            SearchType=PostSearchType,
            SearchCondition=PostSearch,
            Query=True
        )
    else:
        Post = PTTBot.getPost(
            Board,
            PostIndex=NewestIndex,
            Query=True
        )

    CurrentDate_0 = Post.getListDate().replace('/', '').strip()
    if len(CurrentDate_0) < 4:
        CurrentDate_0 = '0' + CurrentDate_0
    CurrentDate_1 = CurrentDate_0
    if len(CurrentDate_1) < 4:
        CurrentDate_1 = '0' + CurrentDate_1

    BiggestTarget = getTarget(CurrentDate_0, CurrentDate_1)
    if show:
        print(f'BiggestTarget {BiggestTarget}')

    Start = findCurrentDateFirst(
        BiggestTarget, NewestIndex, DayAgo, show=False)

    if show:
        print(f'Start {Start}')

    if DayAgo > 0:
        End = findCurrentDateFirst(
            BiggestTarget, NewestIndex, DayAgo - 1, show=False, OldestIndex=Start) - 1
    elif DayAgo == 0:
        End = NewestIndex

    if show:
        print('Result', Start, End)

    return Start, End
