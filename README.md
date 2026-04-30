# epub-to-md

将 EPUB 电子书转换为单文件 Markdown，图片以 base64 内嵌。

## 安装

### 方式一：pip 安装（需 Python 3.11+）

```bash
# 安装
pip install dist/epub_to_md-0.1.0-py3-none-any.whl

# 更新（重新打包后）
pip install --force-reinstall dist/epub_to_md-0.1.0-py3-none-any.whl

# 卸载
pip uninstall epub-to-md
```

### 方式二：独立可执行文件（无需 Python）

```bash
# Mac (x86_64)
cp dist/epub-to-md ~/.local/bin/
```

## 使用

```bash
epub-to-md 书.epub
epub-to-md 书.epub -o 输出.md
```

输出包含：
- YAML 元数据（书名、作者）
- 完整目录层级（从 NCX/Nav 提取）
- 内嵌图片（base64）
- 表格、代码块、脚注等常见格式

## 项目说明

核心逻辑在 `src/epub_to_md/`：

| 模块 | 职责 |
|------|------|
| `epub_parser.py` | 解包 EPUB，提取元数据、章节、图片、目录 |
| `converter.py` | XHTML → Markdown 转换 |
| `image_resolver.py` | 图片 base64 内嵌 |
| `orchestrator.py` | 编排各模块 |
| `cli.py` | 命令行界面 |

## 构建

```bash
python -m build --wheel                    # pip 包
pyinstaller --onefile src/epub_to_md/cli.py  # 独立可执行文件
```
