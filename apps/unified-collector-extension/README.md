# Varla 统一采集 Chrome 插件 / Varla Unified Collector Extension

**简体中文** | [English](README.en.md)

在同一面板切换 KOL 记录与视频采集。

## 运行环境

Chrome/Edge；同时运行本地 8765 和 8766 后端。

## 第一次使用

先解压完整包。以下命令都在**当前程序目录**运行，不要在 ZIP 预览窗口中运行。Windows 用户可在资源管理器打开该目录，在地址栏输入 `powershell` 并按回车。

1. 先按同完整包内 `apps/varla-kol-collector/README.md` 启动完整采集器。
2. 也可双击本目录 `start_varla_unified_collector.bat`，它会查找同级完整采集器。
3. 加载下方扩展目录，在扩展弹窗检查两项服务状态。
4. 打开 Instagram/TikTok/YouTube 页面，使用 Varla 面板，核对后保存。

浏览器打开：`http://127.0.0.1:8766`

### 安装浏览器扩展

1. 打开 Chrome，在地址栏输入 `chrome://extensions/`（Edge 用 `edge://extensions/`）。
2. 打开右上角**开发者模式**，点**加载已解压的扩展程序**。
3. 从当前程序目录进入 `varla_unified_collector_extension_无Moto版`，选择里面直接能看到 `manifest.json` 的文件夹；不要选择 ZIP 或项目最外层。
4. 已打开的网站要刷新一次，再打开插件或侧边面板。支持网站以 manifest 声明为准。
5. 显示本地服务离线时，按上面的步骤启动服务，并保持服务窗口开启。


## 成功后应该看到什么

扩展状态显示两个本地服务可达，保存结果出现在自己的本地输出目录。

## 当前功能边界

Chrome 插件本身不是服务端；只加载扩展而不启动采集器不能写 Excel。

## 常见问题

| 现象 | 处理方法 |
| --- | --- |
| 黑窗口闪退 / 找不到 Python | 在当前目录打开 PowerShell，执行 `python --version`。需要安装时从 python.org 安装并勾选 Add Python to PATH，然后重新运行本文命令看具体错误。 |
| 提示缺少模块 | 用启动程序的同一个 Python 安装该程序 requirements 中的依赖。 |
| 页面打不开 / 端口占用 | 对照本文地址和服务日志；先关闭自己正在使用的冲突工具。浏览器扩展不能替代后端。 |
| Excel 保存失败 | 关闭 Excel/WPS 中的文件，检查输出路径后重试一次。 |
| 登录或飞书权限失败 | 使用自己的配置，检查目标资源权限；不要复制别人的 Token。 |

## 本地数据

账号配置、会话、台账和运行结果由使用者在自己电脑生成或配置。公开源码不附带真实客户/KOL 数据、邮箱内容、合同或已登录账号。
