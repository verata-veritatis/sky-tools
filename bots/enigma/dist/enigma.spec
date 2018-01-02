# -*- mode: python -*-

block_cipher = None


a = Analysis(['enigma.py'],
             pathex=['/Users/mchamerski/Documents/Stratis/stratis'],
             binaries=[],
             datas=[('/Users/mchamerski/Documents/Stratis/stratis','.')],
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
          exclude_binaries=True,
          name='Enigma 1.0.12',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Enigma 1.0.12')
