🐍 Python 包安装助手

一个基于 tkinter 和 pip 的轻量级 Python 包管理工具。提供 GUI 和 CLI 两种模式，旨在简化 Python 库的安装流程，特别适合新手用户、办公自动化开发者以及需要频繁切换国内镜像源的场景。

版本: v2.2  
运行环境: Python 3.6+ (推荐 Python 3.8+)  
依赖: 仅需 Python 标准库，无需安装第三方模块即可运行。

## 🌍 项目背景

本工具旨在解决两大核心难题：

1. **终端命令门槛高**：初学者面临 `pip` 命令无法识别、环境变量配置困难、虚拟环境激活复杂等问题。
2. **官方源下载慢**：PyPI 官方服务器位于海外，国内直接下载经常遭遇网速极慢或超时，而手动切换国内镜像源命令冗长难记。

通过**图形化界面**或**简单命令行**屏蔽底层复杂性，并**内置多镜像源自动尝试**，让 Python 包安装变得简单、快速、稳定。

## ✨ 主要功能

| 功能 | 说明 |
|------|------|
| 🚀 一键安装 | 支持单个或多个包名（空格分隔），自动调用 pip 安装 |
| 📁 requirements.txt | 支持从文件导入包列表（GUI 按钮 / CLI `-r` 参数） |
| 🌏 多镜像源 | 内置清华、阿里、中科大、腾讯、豆瓣、华为云、官方源，依次尝试 |
| 📦 快捷包组 | 预设数据处理、Excel、爬虫、Web、AI、自动化等场景包组合 |
| 🛡️ 智能防错 | 默认 `--user` 避免权限错误，智能识别超时/包不存在 |
| 🔍 安装验证 | 导入检查、pip list、基础功能测试 |
| 🕰️ 历史记录 | 自动保存最近 50 次安装记录 |
| 🎨 高 DPI | 适配高 DPI 屏幕，布局自适应 |

## 📂 项目结构

```
.
├── install_with_mirror.py   # GUI 主程序
├── install_cli.py          # 命令行版（支持 -r requirements.txt）
├── config.py               # 共用配置（镜像、包组、映射）
├── pip_core.py             # 核心安装与验证逻辑
└── README.md
```

注：首次运行 GUI 后会在用户主目录生成 `.pip_gui_history.json` 存储历史记录。

## 🛠️ 快速开始

### GUI 模式（推荐）

```bash
python install_with_mirror.py
```

或在 Windows 资源管理器中双击该文件（若 .py 已关联 Python）。

### CLI 模式（无界面 / 脚本调用）

```bash
# 安装指定包
python install_cli.py pandas openpyxl requests

# 从 requirements.txt 安装
python install_cli.py -r requirements.txt

# 指定 Python 解释器
python install_cli.py --python "C:\Python311\python.exe" pandas

# 安装后验证
python install_cli.py --verify pandas
```

## 💡 使用指南（GUI）

1. **输入包名**：在输入框中输入包名，如 `pandas numpy`
2. **导入 requirements.txt**：点击「📁 导入 requirements.txt」选择文件
3. **快捷组**：点击蓝色标签（如「📊 数据处理」）自动填入相关包
4. **高级选项**：勾选「升级已安装的包」「仅当前用户安装」「安装后验证」
5. **自定义 Python**：留空使用当前环境，或点击「...」选择其他解释器
6. **开始安装**：点击「🚀 开始安装」，观察下方日志

## ⚙️ 技术亮点

- **模块化设计**：`config` / `pip_core` 供 GUI 与 CLI 共用，减少重复
- **多线程**：耗时安装放入后台线程，界面不卡顿
- **零依赖**：仅用 Python 标准库，可打包为 .exe 分发
- **鲁棒编码**：`encoding='utf-8'`、`errors='replace'` 兼容各平台

## ❓ 常见问题

**Q: 点击安装后提示「权限被拒绝」？**  
A: 确保勾选「仅当前用户安装 (--user)」。若需全局安装，请以管理员身份运行。

**Q: torch、tensorflow 等大包安装慢或失败？**  
A: 工具会自动尝试多个镜像。若仍失败，请检查网络，或稍后重试。

**Q: 无图形界面的服务器上怎么用？**  
A: 使用 CLI：`python install_cli.py -r requirements.txt`

## 📄 许可证

本项目采用 MIT License 开源。

## 🤝 贡献与反馈

如有 Bug 或功能建议，欢迎提交 Issue 或 Pull Request。

作者: Lan Yupo  
最后更新: 2026-03-02
