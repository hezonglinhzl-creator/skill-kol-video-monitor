# KOL 记录器 Chrome 插件 / KOL Recorder Chrome Extension

**简体中文** | [English](README.en.md)

在 Instagram/TikTok 创作者主页读取可见字段并写入本地 Excel。

## 运行环境

Windows、Python 3.10+、Chrome 或 Edge、openpyxl。

## 第一次使用

先解压完整包。以下命令都在**当前程序目录**运行，不要在 ZIP 预览窗口中运行。Windows 用户可在资源管理器打开该目录，在地址栏输入 `powershell` 并按回车。

1. 在本目录打开 PowerShell，运行 `python -m pip install -r requirements.txt`。
2. 先运行 `python create_blank_workbook.py`，只在没有台账时生成空白 16 列文件。
3. 双击 `start_kol_recorder.bat`，保留服务窗口。
4. 安装下方扩展后打开创作者主页，先检查识别字段，再点击记录。

浏览器打开：`http://127.0.0.1:8765`

### 安装浏览器扩展

1. 打开 Chrome，在地址栏输入 `chrome://extensions/`（Edge 用 `edge://extensions/`）。
2. 打开右上角**开发者模式**，点**加载已解压的扩展程序**。
3. 从当前程序目录进入 `chrome_kol_recorder_extension`，选择里面直接能看到 `manifest.json` 的文件夹；不要选择 ZIP 或项目最外层。
4. 已打开的网站要刷新一次，再打开插件或侧边面板。支持网站以 manifest 声明为准。
5. 显示本地服务离线时，按上面的步骤启动服务，并保持服务窗口开启。


## 成功后应该看到什么

`outputs/varla_kol_tracker.xlsx` 出现记录；写入时关闭 Excel/WPS。

## 当前功能边界

只读页面可见内容，隐藏邮箱和缺失指标应留空。 仅采集时默认记录为待建联，只有明确传入状态才标记已联系。

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
