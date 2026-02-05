# 快捷记事本 Desktop-writer

一个简单的桌面记事本程序，支持全局快捷键和自动保存功能。同时提供命令行工具（CLI），支持快速添加随笔、管理文件、工作列表等功能。

## 功能特点

- 全局快捷键（Shift+Alt+E）快速唤醒窗口
- 支持文件路径自定义和自动保存
- 支持窗口最小化和快速恢复
- 支持内容全屏查看

## 编译方法

本项目使用 PyInstaller 将 Python 代码打包成独立的 Windows 可执行文件。

### 前置要求

1. **Python 3.6 或更高版本**
2. **安装依赖包**：
   ```bash
   pip install keyboard pywin32 pyinstaller
   ```

### 编译步骤

1. **确保已安装所有依赖**：
   ```bash
   pip install keyboard pywin32 pyinstaller
   ```

2. **关闭正在运行的程序**（如果有）：
   - 确保没有 `texteditor.exe` 进程在运行

3. **执行编译命令**：
   ```bash
   pyinstaller -y texteditor.spec
   ```

   或者使用完整命令（不推荐，建议使用 spec 文件）：
   ```bash
   pyinstaller --hidden-import keyboard --hidden-import win32gui --hidden-import win32con --hidden-import win32com --uac-admin -w texteditor.py
   ```

4. **编译输出**：
   - 编译完成后，可执行文件位于 `dist/texteditor/texteditor.exe`
   - 所有依赖文件都在 `dist/texteditor/` 目录下
   - 可以将整个 `dist/texteditor/` 目录打包分发

### 编译说明

- `texteditor.spec` 是 PyInstaller 的配置文件，包含了所有编译选项
- 编译后的程序需要管理员权限才能使用全局快捷键（`--uac-admin`）
- 程序以窗口模式运行（`-w`，无控制台窗口）
- 所有必要的 tkinter 数据文件已自动包含

### 注意事项

- 编译前请确保所有依赖都已正确安装
- 如果遇到 tkinter 相关错误，检查 Python 安装目录下的 `tcl` 和 `tk` 目录是否存在
- 编译后的程序体积较大（包含 Python 运行时和所有依赖），这是正常的

## 使用说明

### 快捷键

- `Shift + Alt + E`: 全局快捷键，随时唤醒程序窗口
- `Ctrl + S`: 保存当前内容
- `ESC`: 最小化窗口

### 基本操作

1. **文件路径设置**

   - 点击"浏览"选择保存位置
   - 或直接输入文件路径后按回车
2. **内容编辑**

   - 在文本框中输入内容
   - 点击"保存"按钮或使用 Ctrl+S 保存
3. **窗口控制**

   - 点击窗口的关闭按钮(X)会最小化而不是退出
   - 使用 Shift+Alt+E 可随时唤醒窗口
   - 点击"退出程序"按钮完全退出

### 注意事项

1. 程序需要管理员权限才能使用全局快捷键
2. 配置信息保存在 texteditor_config.json 中
3. 关闭窗口只会最小化，需要点击"退出程序"才会完全退出

## CLI 命令行工具使用说明

项目还提供了命令行工具 `texteditor_cli.py`，可以通过命令行快速管理文本文件。

### 前置要求

- Python 3.x
- 已安装项目依赖（`keyboard`, `pywin32` 等）
- Windows PowerShell（推荐配置 `tt` 快捷命令）

### 快速开始

如果已配置 PowerShell 的 `tt` 命令，可以直接使用：

```powershell
# 添加一条随笔
tt add 今天天气真好

# 查看文件路径
tt path

# 查看文件最后20行
tt tail -n 20
```

如果没有配置 `tt` 命令，可以直接使用 Python 运行：

```bash
python texteditor_cli.py add "今天天气真好"
```

### 主要命令

#### 1. `add` - 添加随笔

添加带时间戳的随笔到配置文件中指定的文件。

```powershell
# 添加普通随笔
tt add 今天天气真好

# 添加带标签的随笔
tt add #TODO 完成项目报告
tt add #工作 #重要 明天要开会
```

#### 2. `path` - 管理文件路径

查看或设置配置文件中记录的文件路径。

```powershell
# 查看当前路径
tt path

# 设置新路径
tt path "C:\Users\用户名\Documents\我的日志.txt"
```

#### 3. `head` / `tail` - 查看文件内容

查看文件的前N行或最后N行。

```powershell
# 查看前10行（默认）
tt head

# 查看前20行
tt head -n 20

# 查看最后10行（默认）
tt tail

# 查看最后20行
tt tail -n 20
```

#### 4. `config` - 配置管理

设置配置项（支持嵌套键名）。

```powershell
# 设置 tail 命令的默认行数
tt config tail.n 100

# 之后使用 tail 命令时会自动使用100行
tt tail
```

#### 5. `gui` - 启动 GUI 版本

启动图形界面版本的程序。

```powershell
tt gui
```

#### 6. `csv` - 查看 CSV 文件信息

查看 CSV 文件的基本信息（表头、行数、列数等）。

```powershell
tt csv "工作列表.csv"
```

#### 7. `schedule` - 排期管理

管理时间段、任务和完成情况。

```powershell
# 添加排期
tt schedule add "2025-01-01" "2025-01-31" "完成项目报告" --status "未完成" --description "重要项目"

# 显示排期列表
tt schedule list

# 按状态筛选
tt schedule list --status "进行中"

# 按日期范围筛选
tt schedule list --start-date "2025-01-01" --end-date "2025-01-31"

# 编辑排期
tt schedule edit --id 0 --status "已完成"
tt schedule edit --index 0 --task "更新后的任务"

# 删除排期
tt schedule delete --id 0
tt schedule delete --index 0

# 搜索排期
tt schedule search "项目"
tt schedule search --task "开发"

# 对话式自动生成排期
tt schedule gen
# 会依次询问：
# - 总时长（小时，例如：8）
# - 每个排期的时间单位（例如：1小时、40分钟、1.5小时）
# - 开始时间（可选，留空则从当前时间开始）
# - 任务名称模板（可选，可使用 {n} 表示序号，默认：任务{n}）
#   * 留空：使用默认模板 "任务{n}"，将生成：任务1、任务2、任务3...
#   * 使用 {n} 占位符：例如 "工作{n}" 将生成：工作1、工作2、工作3...
#   * 不使用 {n}：例如 "学习" 将生成：学习、学习、学习...
#   * 示例："第{n}个任务" → 第1个任务、第2个任务、第3个任务...
# - 默认完成情况（已完成/进行中/未完成，默认：未完成）
# - 为每个任务设置详细描述（会依次询问每个任务的描述，可直接回车跳过）
#   * 支持多行输入，使用 \n 表示换行（例如：第一行\n第二行）
```

更多 `schedule` 子命令：
- `tt schedule add <开始时间> <结束时间> <任务> [选项]` - 添加排期
- `tt schedule list [选项]` - 显示排期列表
- `tt schedule edit --id <ID> [选项]` - 编辑排期信息
- `tt schedule delete --id <ID>` - 删除排期
- `tt schedule search [关键词] [选项]` - 搜索排期
- `tt schedule gen` - 对话式自动生成排期任务（会询问总时长、时间单位等信息）

### 配置文件

CLI 工具与 GUI 版本共享配置文件 `texteditor_config.json`，位于脚本所在目录。

配置文件格式：
```json
{
  "file_path": "C:\\projects\\my-blogs\\202512\\日志.txt",
  "tail": {
    "n": 20
  }
}
```

### PowerShell 快捷命令配置

在 PowerShell 配置文件中（`$PROFILE`）配置 `tt` 命令后，可以直接使用：

```powershell
# 查看配置文件位置
echo $PROFILE

# 重新加载配置（修改后）
. $PROFILE
```

详细使用说明请参考 `CLI_README.md`。

## 常见问题

1. **快捷键无响应**

   - 确保以管理员权限运行
   - 检查是否有快捷键冲突
   
2. **保存失败**

   - 检查文件路径权限
   - 确保磁盘空间充足

3. **窗口不能置顶**

   - 重新按 Shift+Alt+E 唤醒
