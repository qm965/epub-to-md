# epub-to-md

将 EPUB 电子书转换为单文件 Markdown，图片以 base64 内嵌。

## 安装

### 方式一：pip 安装（需 Python 3.11+）

```bash
# 从 GitHub 直接安装
python3 -m pip install git+https://github.com/qm965/epub-to-md.git

# 从本地构建产物安装（需先构建，产物在 dist/ 目录）
python3 -m pip install dist/epub_to_md-0.1.0-py3-none-any.whl

# 更新
python3 -m pip install --force-reinstall git+https://github.com/qm965/epub-to-md.git

# 卸载
python3 -m pip uninstall epub-to-md
```

### 方式二：独立可执行文件（无需 Python）

```bash
# Mac (x86_64)
cp dist/epub-to-md ~/.local/bin/
```

之后可在任意目录直接运行。

## 使用

```bash
epub-to-md 书.epub
epub-to-md 书.epub -o 输出.md
```

输出说明：
- 开头为 YAML 元数据（书名、作者、来源）
- 标题层级从 EPUB 原生目录（NCX/Nav）提取，不管原书用 `<h1>` 还是 CSS class
- 图片以内联 base64 嵌入，不产生额外图片文件
- 表格、代码块、脚注等常见格式保留

## 从源码运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "."
epub-to-md 书.epub
```

## 项目结构

核心逻辑在 `src/epub_to_md/`：

| 模块 | 职责 |
|------|------|
| `epub_parser.py` | 解包 EPUB，提取元数据、章节、图片、目录（NCX/Nav） |
| `converter.py` | XHTML → Markdown 转换（含表格、代码、脚注等） |
| `image_resolver.py` | 图片 base64 内嵌 |
| `orchestrator.py` | 编排各模块，注入目录标题 |
| `exceptions.py` | 自定义异常 |
| `cli.py` | 命令行界面 |

## 构建

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. pip 包
python -m build --wheel

# 3. 独立可执行文件
pyinstaller --onefile --name epub-to-md src/epub_to_md/cli.py

# 产物在 dist/ 目录
```
