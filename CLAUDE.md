# epub-to-md

## 项目简介
EPUB 转 Markdown CLI 工具，图片以 base64 内嵌，输出单文件 .md。

## 技术栈
- Python 3.11+
- click (CLI)
- beautifulsoup4 + lxml (HTML/XML 解析)
- ebooklib (EPUB 解包)
- pytest (测试)

## 项目结构
```
src/epub_to_md/
├── cli.py             # 命令行入口
├── converter.py       # XHTML → Markdown 转换
├── epub_parser.py     # EPUB 解包、元数据/章节/图片/目录提取
├── exceptions.py      # 自定义异常
├── image_resolver.py  # 图片 base64 内嵌
└── orchestrator.py    # 编排各模块
tests/                 # pytest 测试
dist/                  # 构建产物（wheel + 可执行文件）
```

## 常用命令
```bash
# 运行测试
python -m pytest -v

# 从源码运行
epub-to-md 书.epub

# 构建 pip 包
python -m build --wheel

# 构建独立可执行文件
pyinstaller --onefile --name epub-to-md src/epub_to_md/cli.py
```

## 注意事项
- NCX/Nav 解析使用 BeautifulSoup XML 模式（`features="xml"`）
- `<item>` 和 `<img>` 属性顺序不固定，解析时按「匹配整标签 → 逐个提取属性」处理
- 标题优先从 NCX/Nav 提取，CSS class 启发式检测作为补充
- Homebrew Python 有 PEP 668 保护，全局安装用 pipx
