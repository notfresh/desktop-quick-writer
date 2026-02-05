# 开发说明

## 环境配置

1. Python 3.6 或更高版本
2. 安装依赖：

```bash
pip install keyboard pywin32
```

## 打包方法

使用 PyInstaller 打包成独立的 exe 程序：

1. 安装 PyInstaller：

```bash
pip install pyinstaller
```

2. 执行打包命令：

2.1 关闭正在运行的 texteditor.exe（如果有）
2.2 然后重新运行编译命令：
pyinstaller -y texteditor.spec


完整的命令是
```bash
pyinstaller --hidden-import keyboard --hidden-import win32gui --hidden-import win32con --hidden-import win32com --uac-admin -w texteditor.py
```

## 项目文件说明

- `texteditor.py`: 主程序源代码
- `texteditor.spec`: PyInstaller 打包配置文件
- `README.md`: 用户使用说明
- `dev.md`: 开发相关说明
- `texteditor_config.json`: 程序配置文件（运行时生成）

## 开发注意事项

1. 全局快捷键需要管理员权限
2. 窗口置顶使用了 win32gui 的 API
3. 文件保存使用 UTF-8 编码
4. 配置文件使用 JSON 格式
