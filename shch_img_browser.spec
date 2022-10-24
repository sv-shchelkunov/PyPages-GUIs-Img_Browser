# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['shch_img_browser.py'],
             pathex=['D:\\PyPages\\GUIs\\Img_Browser'],
             binaries=[],
             datas=[
		('shch_img_browser_cfg/shch_071821_121644.ico','shch_img_browser_cfg'),
		('shch_img_browser_imgs/readme.txt','shch_img_browser_imgs'),
		('shch_img_browser_imgs/bulldozer.jpg','shch_img_browser_imgs'),
		('shch_img_browser_imgs/truck.jpg','shch_img_browser_imgs'),
		('shch_img_browser_imgs/tractor.jpg','shch_img_browser_imgs')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
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
          [],
          exclude_binaries=True,
          name='shch_img_browser',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='shch_img_browser')
