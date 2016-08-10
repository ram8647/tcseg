# -*- mode: python -*-

block_cipher = None


a = Analysis(['main_UI.py'],
             pathex=['/Users/jeremyfisher/Dropbox/Summer 16/TcSeg/TC Model/BatchManager'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main_UI',
          debug=False,
          strip=False,
          upx=True,
          console=True )
