# Code::Blocks 25.03 macOS 修复源码

`codeblocks_25.03/` 是包含修复的完整源码，保留上游版权声明和许可证。`patches/` 是相对于原始 25.03 源码的四份补丁，供维护者审查或应用；当前源码已应用补丁，无需再次执行。

提交上游时可使用 `CHANGE_DESCRIPTION.md` 的英文说明，并提交以下实际改动：

- `src/plugins/codecompletion/` 内插件命名空间、启动生命周期、macOS 链接设置及解析器测试适配。
- `src/sdk/encodingdetector.cpp` 内文件读取与字符转换修复。

`patches/henryye-splash.patch` 是独立的 macOS 启动界面署名补丁，显示“HenryYe修复版 支持新的MacOS”。功能修复的两份补丁可单独提交。

`src/plugins/codecompletion/macos-fix/` 是额外的本机构建辅助脚本和编码回归源码，可以作为附加材料提交；不是核心补丁的必要组成。构建要求见该目录 README。测试副本、编译缓存和二进制产物均未包含在源码目录中。

补丁应用示例（仅用于尚未修复的原始源码，在其根目录执行）：

```sh
patch -p1 < /path/to/patches/plugin-refactor.patch
patch -p1 < /path/to/patches/core-encoding.patch
```

安装成品见同级“安装包”目录。源码目前仅整理在本地，尚未上传或提交到任何平台。

`patches/macos-light-appearance.patch` 固定 macOS 应用为浅色外观。`codeblocks.plist.in` 和已打包应用的 `Info.plist` 均设置 `NSRequiresAquaSystemAppearance=true`；系统设置为暗黑或自动模式时仍使用浅色。此项可独立于崩溃修复提交。
