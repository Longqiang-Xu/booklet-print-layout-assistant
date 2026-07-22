# Booklet Splitter

[English README](README.md)

![Booklet Splitter 主界面](docs/images/app-main.png)

Booklet Splitter 是一个用于 PDF 小册子分册的桌面工具。它适合这样的场景：
你已经有一个按阅读顺序排好的 PDF，想把它拆成若干个较薄的小册子 PDF，
方便后续双面打印、折叠和装订。

当前 `v0.1.0` 是一个刻意收窄功能边界的版本，只专注于 PDF 小册子分册。

## 功能

- 按“每册最多 N 张纸”拆分 PDF。
- 按“固定分成 K 册”拆分 PDF。
- 每册使用连续的源页范围。
- 自动把每册补齐到 4 的倍数页。
- 生成分册 PDF。
- 生成 `打印清单.txt` 和 `manifest.txt`。
- 提供 pywebview 桌面界面。
- 提供命令行入口，方便自动化。

## 暂不支持

- EPUB/CBZ 转 PDF。
- 自动识别彩页。
- 黑白/彩色打印文件拆分。
- 打印机队列管理。
- SumatraPDF 一键打印。
- 真正的 A4 2-up 小册子拼版 PDF。

目前工具生成的是“连续页范围 + 补空白页”的分册 PDF。实际的小册子版面、
双面打印、长边/短边翻转等设置，仍由打印机驱动或其他拼版工具处理。

## 分册规则

每 1 张纸对应 4 个 PDF 页位：

```text
总纸张数 = ceil(总页数 / 4)
```

按“每册最多 N 张纸”拆分时，工具会先计算需要几册，再尽量平均分配纸张。

示例：

```text
160 页 -> 40 张纸
每册最多 14 张纸 -> 3 册
纸张分配 -> 14 / 13 / 13
```

按“固定分成 K 册”拆分时，工具会把总纸张数尽量平均分给这些册。

示例：

```text
168 页 -> 42 张纸
固定分成 4 册 -> 11 / 11 / 10 / 10
```

最后一册如果源页不足，会自动补空白页。

## 开发安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

## 运行桌面应用

```powershell
booklet-splitter
```

如果当前 shell 找不到安装后的脚本，可以用：

```powershell
python -m booklet_splitter
```

## 命令行使用

```powershell
booklet-split input.pdf --max-sheets 14
booklet-split input.pdf --booklet-count 3
booklet-split input.pdf --booklet-count 3 --output-dir output
```

也可以使用：

```powershell
python -m booklet_splitter.cli input.pdf --max-sheets 14
```

## 示例 PDF

生成示例 PDF：

```powershell
python .\scripts\create_example_pdf.py
```

默认输出：

```text
examples\sample-17-pages.pdf
```

试着拆分：

```powershell
booklet-split examples\sample-17-pages.pdf --booklet-count 2
```

## Windows 打包

```powershell
.\scripts\build_windows.ps1
```

脚本会先创建干净的 `.venv-build` 环境，再用 PyInstaller 打包，避免把
Anaconda 或全局 Python 环境里的无关依赖带进发布包。

打包后的目录：

```text
dist\BookletSplitter\
```

运行：

```text
dist\BookletSplitter\BookletSplitter.exe
```

## 生成 Release Zip

打包完成后运行：

```powershell
.\scripts\package_release.ps1
```

生成：

```text
release\BookletSplitter-v0.1.0-windows-x64.zip
```

## 项目结构

```text
src/booklet_splitter/core/      PDF 分册逻辑和清单生成
src/booklet_splitter/app/       pywebview 桌面集成
src/booklet_splitter/frontend/  HTML/CSS/JS 界面
tests/                          测试
scripts/                        开发和打包脚本
```

## 路线图

- 补充更多截图。
- 增加更多无版权示例 PDF。
- 增加真正的 A4 2-up 小册子拼版。
- 重新引入可选彩页工作流。
- 增加安装包形式发布。

## 许可证

MIT。
