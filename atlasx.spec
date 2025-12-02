# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for AtlasXbrowser (One Directory Mode)

import os
from pathlib import Path

# 获取当前工作目录
proj = Path(os.getcwd())

block_cipher = None

# 1. Analysis: 分析代码和依赖
a = Analysis(
    scripts=[str(proj / "ABrowser.py")],
    pathex=[str(proj)],
    binaries=[],
    datas=[
        (str(proj / "atlasbg.png"), "."),
        (str(proj / "rotateleft.png"), "."),
        (str(proj / "rotateright.png"), "."),
        (str(proj / "colorbar.png"), "."),
        # 文件夹打包
        (str(proj / "Azure-ttk-theme"), "Azure-ttk-theme"),
        (str(proj / "barcode_files"), "barcode_files"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

# 2. PYZ: 压缩 Python 代码
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 3. EXE: 生成主执行程序 (不包含依赖库)
exe = EXE(
    pyz,
    a.scripts,
    [], # 注意：这里留空
    exclude_binaries=True, # 🔥 关键设置：排除二进制文件，让它们去文件夹里
    name='AtlasXbrowser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)

# 4. COLLECT: 收集所有文件到一个文件夹
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AtlasXbrowser', # 这是 dist 下生成的文件夹名字
)