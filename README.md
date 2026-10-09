# Code::Blocks 25.03 — macOS Fix

**A community-maintained macOS compatibility fix for Code::Blocks 25.03.**

修复 Code::Blocks 25.03 在新版 macOS 上的启动崩溃问题，保留并修复 Code Completion（代码自动补全）插件，而不是简单地将其删除或禁用。

> ⚠️ 本项目为个人维护的非官方修复版本，与 Code::Blocks 官方开发团队无隶属关系。

## 项目简介 | Overview

Code::Blocks 是一款免费、开源、跨平台的 C/C++ 集成开发环境（IDE）。

在部分较新的 macOS 环境中，Code::Blocks 25.03 可能出现启动崩溃、插件初始化失败以及文件编码转换异常等问题。

本项目基于 Code::Blocks 25.03 原始源码进行修复，重点解决 macOS 平台上的兼容性问题，并尽可能保留原有功能。

**Unlike workarounds that simply disable the Code Completion plugin, this project fixes its initialization and lifecycle handling while preserving the plugin's functionality.**

## 主要修复 | Key Fixes

### 1. Code Completion 插件修复

- 调整插件命名空间及相关实现
- 修复插件启动生命周期中的初始化问题
- 适配 macOS 平台的链接配置
- 调整相关解析器测试
- 保留代码自动补全功能，而非直接禁用插件

### 2. 文件编码处理修复

修复 `src/sdk/encodingdetector.cpp` 中的文件读取和字符转换相关问题。

旨在减少部分文件编码处理过程中出现的异常及崩溃。

### 3. macOS 外观兼容性

通过 `NSRequiresAquaSystemAppearance` 设置，使应用在 macOS 深色模式或自动外观模式下仍使用浅色界面。

此修改与核心崩溃修复相互独立。

### 4. 启动界面调整

增加独立的 macOS 启动界面署名补丁，以便区分本修复版本与官方原版。

此项属于外观定制，不影响核心功能修复。

## 下载与安装 | Download & Installation

请前往 GitHub Releases 页面获取已发布的安装包：

**[Download from GitHub Releases](https://github.com/HenryYe07/Code-Block-MacOS-FIX/releases)**

安装步骤：

1. 打开 Releases 页面，选择适合自己设备的发行版本。
2. 下载对应的 macOS 安装包。
3. 按发行页面的说明安装应用。
4. 启动 Code::Blocks 并进行测试。

**注意：** 不同 macOS 版本及处理器架构的兼容性可能存在差异。具体支持范围以各版本的 Release Notes 为准。

## 源码结构 | Repository Structure

```text
Code-Block-MacOS-FIX/
├── codeblocks_25.03/       # 已应用修复的完整源码
├── patches/                # 相对于官方源码的补丁
├── CHANGE_DESCRIPTION.md   # 英文修改说明
├── LICENSE                 # GPL-3.0 许可证
└── README.md
```

`codeblocks_25.03/` 包含已经应用修复的完整源码，**无需重复应用补丁**。

`patches/` 则提供独立补丁，方便开发者审查代码、复现修改或向上游项目提交修复。

## 补丁说明 | Patches

| 补丁文件 | 作用 |
|---|---|
| `plugin-refactor.patch` | Code Completion 插件重构及兼容性修复 |
| `core-encoding.patch` | 文件编码处理修复 |
| `macos-light-appearance.patch` | macOS 浅色外观适配 |
| `henryye-splash.patch` | 启动界面署名修改 |

其中，插件修复与编码修复可以独立于外观定制提交至上游项目。

### 应用补丁

如果需要将修复应用到未经修改的 Code::Blocks 25.03 原始源码，可在原始源码根目录执行：

```bash
patch -p1 < /path/to/patches/plugin-refactor.patch
patch -p1 < /path/to/patches/core-encoding.patch
```

请将 `/path/to/patches/` 替换为实际补丁路径。

**不要对本仓库 `codeblocks_25.03/` 目录重复执行上述命令。**

## 编译与开发 | Building from Source

本仓库提供完整的修复后源码。

macOS 相关构建辅助脚本和编码回归测试源码位于：

```text
codeblocks_25.03/src/plugins/codecompletion/macos-fix/
```

具体构建要求请参考该目录内的 README。

构建前请确认已经安装适当的开发工具及所需依赖。不同 macOS 版本和构建环境可能需要额外配置。

## 已知限制 | Known Limitations

- 本项目不是 Code::Blocks 官方发行版。
- 不保证兼容所有 macOS 版本及硬件架构。
- 尚未覆盖所有插件及全部使用场景。
- 后续 macOS 或 Code::Blocks 更新可能引入新的兼容性问题。

如果遇到崩溃或其他异常，欢迎提交 Issue，并尽可能附上 macOS 版本、处理器架构、复现步骤及崩溃日志。

**[Report an Issue](https://github.com/HenryYe07/Code-Block-MacOS-FIX/issues)**

## 上游项目 | Upstream Project

本项目基于 Code::Blocks 25.03 开发。

Code::Blocks 官方网站：

https://www.codeblocks.org/

感谢 Code::Blocks 开发团队及所有开源贡献者。

本项目旨在改善 Code::Blocks 在新版 macOS 上的可用性，同时保持相关修改公开、可审查、可复现。

## 开源许可证 | License

本项目基于 Code::Blocks 原始源码修改，遵循适用的 GNU General Public License 条款。

仓库中提供的 `LICENSE` 文件采用 **GPL-3.0**，原始上游源码中的版权声明和许可证信息予以保留。

各组件仍应遵守其适用的原始许可证及版权声明。

详见 [LICENSE](LICENSE)。

## 维护者 | Maintainer

**HenryYe**

GitHub: [@HenryYe07](https://github.com/HenryYe07)

本项目由个人独立维护，欢迎通过 Issues 和 Pull Requests 反馈问题或贡献代码。

---

**If this project helps you run Code::Blocks on your Mac, consider giving it a ⭐!**

如果这个项目帮助你解决了 Code::Blocks 在 macOS 上的运行问题，欢迎点一个 Star！
