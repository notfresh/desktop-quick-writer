# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

# 获取 Python 安装目录
python_dir = os.path.dirname(sys.executable)

# 收集 tkinter 的数据文件
tkinter_datas = collect_data_files('tkinter')

# 手动添加 tcl 和 tk 数据文件，使用 PyInstaller 期望的目录名称
tcl_dir = os.path.join(python_dir, 'tcl')
tkinter_datas_tcl = []
tkinter_datas_tk = []

if os.path.exists(tcl_dir):
    # 添加 tcl8.6 目录，目标目录名为 _tcl_data（PyInstaller 运行时钩子期望的名称）
    tcl86_dir = os.path.join(tcl_dir, 'tcl8.6')
    if os.path.exists(tcl86_dir):
        tkinter_datas_tcl.append((tcl86_dir, '_tcl_data'))
    
    # 添加 tk8.6 目录，目标目录名为 _tk_data（PyInstaller 运行时钩子期望的名称）
    tk86_dir = os.path.join(tcl_dir, 'tk8.6')
    if os.path.exists(tk86_dir):
        tkinter_datas_tk.append((tk86_dir, '_tk_data'))

# 强制包含 tkinter 模块目录
tkinter_lib_dir = os.path.join(python_dir, 'lib', 'tkinter')
tkinter_module_datas = []
if os.path.exists(tkinter_lib_dir):
    # 将整个 tkinter 目录作为数据文件包含，保持目录结构
    tkinter_module_datas.append((tkinter_lib_dir, 'tkinter'))

a = Analysis(
    ['texteditor.py'],
    pathex=[],
    binaries=[],
    datas=tkinter_datas + tkinter_datas_tcl + tkinter_datas_tk + tkinter_module_datas,
    hiddenimports=['keyboard', 'win32gui', 'win32con', 'win32com', 'tkinter', '_tkinter', 'tkinter.messagebox', 'tkinter.filedialog'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='texteditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='texteditor',
)
