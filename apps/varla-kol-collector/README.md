# KOL 与爆款视频完整采集器 / KOL and Viral Video Collector Kit

**简体中文** | [English](README.en.md)

同时启动 KOL 记录服务和视频采集中心，配套右侧 Varla 浏览器面板。

## 运行环境

Windows、Python 3.10+、Chrome/Edge；首次安装依赖需要网络。

## 第一次使用

先解压完整包。以下命令都在**当前程序目录**运行，不要在 ZIP 预览窗口中运行。Windows 用户可在资源管理器打开该目录，在地址栏输入 `powershell` 并按回车。

1. 双击 `Install_Environment.bat` 安装环境。
2. 在 `KOL_recorder` 内运行 `python create_blank_workbook.py` 创建自己的空白台账。
3. 回到本目录，双击 `Start_Varla_Collector.bat`。
4. 保留两个服务窗口：KOL 8765、视频 8766。
5. 加载 `chrome_extension`，打开目标网站，检查面板内容后记录。

浏览器打开：`http://127.0.0.1:8766`

### 安装浏览器扩展

1. 打开 Chrome，在地址栏输入 `chrome://extensions/`（Edge 用 `edge://extensions/`）。
2. 打开右上角**开发者模式**，点**加载已解压的扩展程序**。
3. 从当前程序目录进入 `chrome_extension`，选择里面直接能看到 `manifest.json` 的文件夹；不要选择 ZIP 或项目最外层。
4. 已打开的网站要刷新一次，再打开插件或侧边面板。支持网站以 manifest 声明为准。
5. 显示本地服务离线时，按上面的步骤启动服务，并保持服务窗口开启。


## 成功后应该看到什么

KOL 记录位于 `KOL_recorder/outputs`，视频结果位于 `viral_video_finder/outputs`。

## 当前功能边界

没有预装真实联系人或结果 Excel；首次需自行初始化台账。

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
