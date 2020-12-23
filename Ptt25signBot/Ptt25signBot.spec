# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Ptt25signBot.py'],
             pathex=[
             'D:\\Git\\PTTBots\\Ptt25signBot',
             'D:\\Git\\PTTBots\\venv\\Lib\\site-packages'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Ptt25signBot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
