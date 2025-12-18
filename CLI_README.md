# texteditor_cli 命令行工具使用说明

## 简介

`texteditor_cli.py` 是一个命令行工具，用于快速管理文本编辑器配置文件指定的文件。支持添加带时间戳的随笔、查看文件内容、管理文件路径等功能。

## 功能特性

- ✅ 快速添加带时间戳的随笔
- ✅ 支持标签系统（以 `#` 开头）
- ✅ 查看文件内容（head/tail）
- ✅ 管理配置文件中的文件路径
- ✅ 自动创建目录
- ✅ 与 GUI 版本共享配置文件

## 安装和配置

### 前置要求

- Python 3.x
- Windows PowerShell（已配置 `tt` 快捷命令）

### PowerShell 快捷命令配置

在 PowerShell 配置文件中（`$PROFILE`）已配置 `tt` 命令，可以直接使用：

```powershell
# 查看配置文件位置
echo $PROFILE

# 重新加载配置（修改后）
. $PROFILE
```

`tt` 命令会自动解析包含 `#` 的参数，无需使用引号。

## 命令详解

### 1. `add` - 添加随笔

添加带时间戳的随笔到配置文件中指定的文件。

**语法：**
```bash
tt add [内容...]
```

**参数：**
- `content`：随笔内容，可以是多个单词，用空格分隔

**特性：**
- 自动添加时间戳（格式：`YYYY-MM-DD HH:MM:SS`）
- 支持标签（以 `#` 开头）
- 自动创建目录（如果不存在）
- 追加模式，不会覆盖原有内容

**示例：**

```powershell
# 添加普通随笔
tt add 今天天气真好

# 添加带单个标签的随笔
tt add #TODO 我勒个去

# 添加带多个标签的随笔
tt add #工作 #重要 完成项目报告

# 添加多词内容
tt add 今天学习了 Python 感觉很有收获
```

**保存格式：**

带标签：
```
[2025-12-18 10:45:13] #TODO
我勒个去
```

不带标签：
```
[2025-12-18 10:45:21]
今天天气真好
```

---

### 2. `path` - 管理文件路径

查看或设置配置文件中记录的文件路径。

**语法：**
```bash
# 查看当前路径
tt path

# 设置新路径
tt path <新路径>
```

**示例：**

```powershell
# 查看当前配置的文件路径
tt path

# 设置新的文件路径
tt path "C:/Users/用户名/Documents/我的日志.txt"
tt path C:\Users\用户名\Documents\我的日志.txt
```

**输出示例：**
```
当前文件路径：C:\projects\my-blogs\2412卷\日志.txt
文件存在：是
文件大小：4323 字节
```

---

### 3. `head` - 查看文件开头

显示配置文件指定文件的前 N 行（类似 Unix `head` 命令）。

**语法：**
```bash
tt head [-n <行数>]
```

**参数：**
- `-n, --lines`：要显示的行数（默认：10）

**示例：**

```powershell
# 显示前10行（默认）
tt head

# 显示前20行
tt head -n 20
tt head --lines 20
```

**输出示例：**
```
4.17 8.52
修改文件类型。

2025.4.15 8.33 
添加了多行逻辑。

... (共 213 行，显示前 10 行)
```

---

### 4. `tail` - 查看文件结尾

显示配置文件指定文件的最后 N 行（类似 Unix `tail` 命令）。

**语法：**
```bash
tt tail [-n <行数>]
```

**参数：**
- `-n, --lines`：要显示的行数（默认：10）

**示例：**

```powershell
# 显示最后10行（默认）
tt tail

# 显示最后20行
tt tail -n 20
tt tail --lines 20
```

**输出示例：**
```
[2025-12-18 10:45:13] #TODO
我勒个去

[2025-12-18 10:45:21]
今天天气真好
... (共 213 行，显示最后 10 行)
```

---

## 配置文件

### 配置文件位置

配置文件 `texteditor_config.json` 位于脚本所在目录（`C:\projects\desktop-writer\`），与 GUI 版本共享。

### 配置文件格式

```json
{
  "file_path": "C:/Users/用户名/projects/my-blogs/2412卷/日志.txt"
}
```

### 配置文件特点

- 使用 UTF-8 编码
- 路径支持正斜杠 `/` 和反斜杠 `\`
- 与 `texteditor.py` GUI 版本共享配置
- 脚本会自动基于脚本目录查找配置文件，不受当前工作目录影响

---

## 使用技巧

### 1. 标签系统

标签以 `#` 开头，可以添加多个标签：

```powershell
tt add #工作 #重要 #紧急 完成项目报告
```

标签会显示在时间戳后面，便于分类和检索。

### 2. 多词内容

多个单词会自动用空格连接：

```powershell
tt add 今天 学习了 Python 感觉 很有 收获
# 保存为：今天 学习了 Python 感觉 很有 收获
```

### 3. 快速查看最新内容

使用 `tail` 命令快速查看最近添加的随笔：

```powershell
tt tail -n 5  # 查看最后5条
```

### 4. 跨目录使用

由于配置文件路径基于脚本目录，可以在任何目录下使用 `tt` 命令：

```powershell
cd C:\Users\zhengxu
tt add 从任何目录都可以使用
```

---

## 常见问题

### Q1: 提示"配置文件中没有设置文件路径"

**原因：** 配置文件不存在或文件路径为空。

**解决方法：**
```powershell
# 设置文件路径
tt path "C:/path/to/your/file.txt"
```

### Q2: 添加随笔后文件没有更新

**可能原因：**
1. 文件路径错误
2. 没有写入权限
3. 磁盘空间不足

**解决方法：**
```powershell
# 检查文件路径
tt path

# 检查文件是否存在
tt head -n 1
```

### Q3: PowerShell 中 `#` 被当作注释

**说明：** 这是正常的 PowerShell 行为。`tt` 函数已特殊处理，可以直接使用：

```powershell
# 这样使用即可，无需引号
tt add #TODO 我勒个去
```

### Q4: 如何查看所有命令帮助

```powershell
# 查看主帮助
tt --help

# 查看具体命令帮助
tt add --help
tt head --help
```

### Q5: 配置文件在哪里？

配置文件位于脚本所在目录：
- 脚本路径：`C:\projects\desktop-writer\texteditor_cli.py`
- 配置文件：`C:\projects\desktop-writer\texteditor_config.json`

---

## 工作流程示例

### 日常使用流程

```powershell
# 1. 设置文件路径（首次使用）
tt path "C:/Users/用户名/Documents/日记.txt"

# 2. 添加随笔
tt add #工作 完成项目文档
tt add #学习 Python 装饰器
tt add 今天天气不错

# 3. 查看最新内容
tt tail -n 5

# 4. 查看文件开头
tt head -n 10
```

### 标签分类示例

```powershell
# 工作相关
tt add #工作 #会议 讨论项目进度
tt add #工作 #待办 完成代码审查

# 学习相关
tt add #学习 #Python 学习了列表推导式
tt add #学习 #读书 《Python编程从入门到实践》

# 生活相关
tt add #生活 今天去公园散步
tt add #生活 #购物 买了新书
```

---

## 技术细节

### 时间戳格式

- 格式：`YYYY-MM-DD HH:MM:SS`
- 示例：`2025-12-18 10:45:13`
- 时区：系统本地时间

### 文件编码

- 配置文件：UTF-8
- 目标文件：UTF-8
- 自动处理编码问题

### 路径处理

- 自动规范化路径（`os.path.normpath`）
- 支持 Windows 路径格式
- 自动创建不存在的目录

---

## 更新日志

### v1.0
- ✅ 基础添加随笔功能
- ✅ 标签系统支持
- ✅ head/tail 命令
- ✅ 路径管理功能
- ✅ PowerShell 快捷命令支持

---

## 许可证

与主项目相同。

---

## 反馈和支持

如有问题或建议，请查看主项目 README 或提交 Issue。

