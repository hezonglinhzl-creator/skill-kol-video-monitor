# KOL 视频采集与数据监控 / KOL Video Collection and Monitoring

**简体中文** | [English](README.en.md)

通过浏览器扩展收集公开内容，在本地整理当前播放、粉丝、点赞和评论，再按配置导出或同步。

## 功能特性

- KOL 与视频采集扩展、完整采集后端
- Instagram shortcode 精确匹配与本地 SQLite 记录
- 输入文件驱动的指标更新、KOL 汇总与同步数据导出

## 这个包里有什么

| 内容 | 位置 |
| --- | --- |
| KOL 与爆款视频完整采集器 | [varla-kol-collector](../../apps/varla-kol-collector/README.md) |
| Instagram 当前指标监控核心 | [varla-instagram-monitor](../../apps/varla-instagram-monitor/README.md) |
| KOL 记录器 Chrome 插件 | [kol-recorder-extension](../../apps/kol-recorder-extension/README.md) |
| Varla 统一采集 Chrome 插件 | [unified-collector-extension](../../apps/unified-collector-extension/README.md) |
| Skill 指令 | [SKILL.md](./SKILL.md) |

## 1. 先准备程序

推荐先只启动完整 varla-kol-collector 采集器。独立 KOL 记录器是备用入口，不要再同时占用 8765 端口；同类采集扩展也先只加载一个版本。

### KOL 与爆款视频完整采集器 (`varla-kol-collector`)

Windows、Python 3.10+、Chrome/Edge；首次安装依赖需要网络。

先进入 `../../apps/varla-kol-collector`。同时启动 KOL 记录服务和视频采集中心，配套右侧 Varla 浏览器面板。

1. 双击 `Install_Environment.bat` 安装环境。
2. 在 `KOL_recorder` 内运行 `python create_blank_workbook.py` 创建自己的空白台账。
3. 回到本目录，双击 `Start_Varla_Collector.bat`。
4. 保留两个服务窗口：KOL 8765、视频 8766。
5. 加载 `chrome_extension`，打开目标网站，检查面板内容后记录。

本地地址：`http://127.0.0.1:8766`

[查看完整程序与浏览器插件安装说明](../../apps/varla-kol-collector/README.md)

没有预装真实联系人或结果 Excel；首次需自行初始化台账。

### Instagram 当前指标监控核心 (`varla-instagram-monitor`)

Python 3.10+；标准库即可处理本地输入，飞书同步另需配置。

先进入 `../../apps/varla-instagram-monitor`。按 shortcode 维护当前指标、首次发现和最后检查时间，再聚合 KOL。

1. 先由采集器获取真实数据，参照源码 README 里的字段结构准备 JSON。
2. 把发现记录存为 `data/discovery_input.json`，更新记录存为 `data/update_input.json`；需要时自行创建 data 目录。
3. 在本目录运行 `python main.py discover`，然后运行 `python main.py update`。
4. 需要导出同步数据时运行 `python main.py sync`；若未配置 sync_feishu.py，只会产生本地同步载荷。

[查看完整程序与浏览器插件安装说明](../../apps/varla-instagram-monitor/README.md)

该核心不会独立登录或实时抓取 Instagram。缺失播放量不会写成 0。

### KOL 记录器 Chrome 插件 (`kol-recorder-extension`)

Windows、Python 3.10+、Chrome 或 Edge、openpyxl。

先进入 `../../apps/kol-recorder-extension`。在 Instagram/TikTok 创作者主页读取可见字段并写入本地 Excel。

1. 在本目录打开 PowerShell，运行 `python -m pip install -r requirements.txt`。
2. 先运行 `python create_blank_workbook.py`，只在没有台账时生成空白 16 列文件。
3. 双击 `start_kol_recorder.bat`，保留服务窗口。
4. 安装下方扩展后打开创作者主页，先检查识别字段，再点击记录。

本地地址：`http://127.0.0.1:8765`

[查看完整程序与浏览器插件安装说明](../../apps/kol-recorder-extension/README.md)

只读页面可见内容，隐藏邮箱和缺失指标应留空。

### Varla 统一采集 Chrome 插件 (`unified-collector-extension`)

Chrome/Edge；同时运行本地 8765 和 8766 后端。

先进入 `../../apps/unified-collector-extension`。在同一面板切换 KOL 记录与视频采集。

1. 先按同完整包内 `apps/varla-kol-collector/README.md` 启动完整采集器。
2. 也可双击本目录 `start_varla_unified_collector.bat`，它会查找同级完整采集器。
3. 加载下方扩展目录，在扩展弹窗检查两项服务状态。
4. 打开 Instagram/TikTok/YouTube 页面，使用 Varla 面板，核对后保存。

本地地址：`http://127.0.0.1:8766`

[查看完整程序与浏览器插件安装说明](../../apps/unified-collector-extension/README.md)

Chrome 插件本身不是服务端；只加载扩展而不启动采集器不能写 Excel。

## 3. 第一次怎么用

| 准备项 | 内容 |
| --- | --- |
| 输入 | 你有权限访问的创作者主页、帖子链接和最新指标 JSON。 |
| 输出 | 本地台账、SQLite 当前指标、KOL 汇总和飞书同步数据。 |

```text
使用 KOL视频抓取监控，先检查采集服务和输入文件，只处理我提供的这 3 个帖子；先给本地结果，不写飞书。
```


## 当前限制与常见问题

监控 main.py 读取输入文件；没有刷新采集数据时，运行 all 不等于完成实时抓取。飞书写入还需要自己的配置及同步助手。

| 问题 | 怎么处理 |
| --- | --- |
| 找不到 Skill | 检查安装窗口结果和目标 SKILL.md，重新打开 Codex 并新建对话。 |
| 程序启动失败 | 在程序目录打开 PowerShell 运行本文命令，让错误保留在窗口，再对照对应程序 README。 |
| 网页看不到插件 | 确认选中直接包含 manifest.json 的目录、网站受支持，并刷新网页。 |
| 外部服务不可用 | 配置自己的授权并检查资源权限；保留本地结果，不把失败说成同步/发送成功。 |

## 隐私与验证范围

这是程序源码与 Skill 分发包，不附带真实账号、OAuth 令牌、客户/KOL 台账、合同、订单、邮箱导出或业务媒体。服务需使用自己的配置。已检查文档和包内入口；此次文档核对没有执行真实下单、发邮件或发布内容。
