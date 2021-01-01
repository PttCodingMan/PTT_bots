import sys
from os import walk


def readFile(fname, func, encoding):
    with open(fname, 'r', encoding=encoding) as fobj:
        content = fobj.read()
        if func in content:
            print(f'[{encoding}] {fname}')
            print(f'找到 {func}')


count = 0


def FindStrInFile(path, func):

    result = []

    f = []
    d = []
    fullpath = None
    for (dirpath, dirnames, filenames) in walk(path):
        fullpath = dirpath
        d.extend(dirnames)
        f.extend(filenames)
        break
    if '.git' in d:
        d.remove('.git')

    if '.gitattributes' in f:
        f.remove('.gitattributes')
    if '.gitignore' in f:
        f.remove('.gitignore')

    if len(f) == 0:
        return

    f = [f'{fullpath}/{x}' for x in f if '.tar' not in x]
    # print('\n'.join(f))
    # print('\n'.join(d))
    # print(fullpath)
    # print(d)
    global count
    count += len(f)

    for fname in f:
        try:
            readFile(fname, func, 'Big5')
        except UnicodeDecodeError:
            pass

        try:
            readFile(fname, func, 'Utf-8')
        except UnicodeDecodeError:
            # print(f'{fname} decode error')
            pass

                # sys.exit()

    for subpath in d:
        FindStrInFile(f'{fullpath}/{subpath}', func)


FindStrInFile('D:/Git/pttbbs', '儲存檔案')
print(count)
