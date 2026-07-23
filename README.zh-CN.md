# Booklet Print Layout Assistant

[English README](README.md)

<p align="center">
  <img src="docs/images/app-main-readme.png" alt="Booklet Print Layout Assistant 主界面" width="100%">
</p>

Booklet Print Layout Assistant，中文名“小册子打印排版助手”，是一个用于准备
小册子打印文件的桌面工具。当前版本先聚焦这样的场景：你已经有一个按阅读顺序
排好的 PDF，想把它拆成若干个较薄的小册子 PDF，方便后续双面打印、折叠和装订。

当前支持以 PDF 为输入，完成页面筛选、小册子分册、空白页补齐和打印清单生成。
后续可以继续扩展 EPUB、CBZ、图片等来源，以及真正的小册子拼版。

## 功能

- 按“每册最多 N 张纸”拆分 PDF。
- 按“固定分成 K 册”拆分 PDF。
- 支持保留或剔除指定页面后再生成分册。
- 每册使用连续的源页范围。
- 自动把每册补齐到 4 的倍数页。
- 生成分册 PDF。
- 生成 `打印清单.txt` 和 `manifest.txt`。
- 提供 pywebview 桌面界面。
- 提供命令行入口，方便自动化。

## 支持范围

当前支持：

- PDF 小册子分册。
- 页面选择。
- 自动补齐空白页。
- 打印清单生成。
- 桌面界面和命令行入口。

后续计划支持：

- EPUB/CBZ 转 PDF。
- 自动识别彩页。
- 黑白/彩色打印文件拆分。
- 打印机队列管理。
- SumatraPDF 一键打印。
- 真正的 A4 2-up 小册子拼版 PDF。

目前输出的是“连续页范围 + 补空白页”的分册 PDF。实际的小册子版面、双面打印、
长边/短边翻转等设置，可以继续交给打印机驱动或其他拼版工具处理。

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
booklet-print-layout-assistant
```

如果当前 shell 找不到安装后的脚本，可以用：

```powershell
python -m booklet_print_layout_assistant
```

## 命令行使用

```powershell
booklet-print input.pdf --max-sheets 14
booklet-print input.pdf --booklet-count 3
booklet-print input.pdf --booklet-count 3 --output-dir output
booklet-print input.pdf --pages "1-20,25,-3" --max-sheets 14
```

也可以使用：

```powershell
python -m booklet_print_layout_assistant.cli input.pdf --max-sheets 14
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
booklet-print examples\sample-17-pages.pdf --booklet-count 2
```

## Windows 打包

```powershell
.\scripts\build_windows.ps1
```

脚本会先创建干净的 `.venv-build` 环境，再用 PyInstaller 打包，避免把
Anaconda 或全局 Python 环境里的无关依赖带进发布包。

打包后的目录：

```text
dist\BookletPrintLayoutAssistant\
```

运行：

```text
dist\BookletPrintLayoutAssistant\BookletPrintLayoutAssistant.exe
```

## 生成 Release Zip

打包完成后运行：

```powershell
.\scripts\package_release.ps1
```

生成：

```text
release\BookletPrintLayoutAssistant-v0.1.0-windows-x64.zip
```

## 项目结构

```text
src/booklet_print_layout_assistant/core/      PDF 分册逻辑和清单生成
src/booklet_print_layout_assistant/app/       pywebview 桌面集成
src/booklet_print_layout_assistant/frontend/  HTML/CSS/JS 界面
tests/                          测试
scripts/                        开发和打包脚本
```

## GitHub 检索建议

建议仓库名：

```text
booklet-print-layout-assistant
```

建议 topics：

```text
pdf, booklet, booklet-printing, pdf-splitter, printing, bookbinding,
imposition, desktop-app, windows, pywebview, pypdf
```

## 路线图

- 增加真正的 A4 2-up 小册子拼版。
- 重新引入可选彩页工作流。
- 增加 EPUB、CBZ、图片来源工作流。
- 增加安装包形式发布。

## 许可证

MIT。
