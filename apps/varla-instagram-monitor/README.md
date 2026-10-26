# Instagram 当前指标监控核心 / Instagram Current Metrics Core

**简体中文** | [English](README.en.md)

按 shortcode 维护当前指标、首次发现和最后检查时间，再聚合 KOL。

## 运行环境

Python 3.10+；标准库即可处理本地输入，飞书同步另需配置。

## 第一次使用

先解压完整包。以下命令都在**当前程序目录**运行，不要在 ZIP 预览窗口中运行。Windows 用户可在资源管理器打开该目录，在地址栏输入 `powershell` 并按回车。

1. 先由采集器获取真实数据，参照源码 README 里的字段结构准备 JSON。
2. 把发现记录存为 `data/discovery_input.json`，更新记录存为 `data/update_input.json`；需要时自行创建 data 目录。
3. 在本目录运行 `python main.py discover`，然后运行 `python main.py update`。
4. 需要导出同步数据时运行 `python main.py sync`；若未配置 sync_feishu.py，只会产生本地同步载荷。

### 输入记录示例

```json
{
  "username": "sample_creator",
  "profile_url": "https://www.instagram.com/sample_creator/",
  "post_url": "https://www.instagram.com/reel/SHORTCODE/",
  "shortcode": "SHORTCODE",
  "followers": 12000,
  "views": 3456,
  "likes": 120,
  "comments": 8,
  "view_status": "OK"
}
```

多条记录放在 JSON 数组中。所有示例数值都要换成对应帖子的真实采集值。

## 成功后应该看到什么

`data/varla_monitor.sqlite3` 和 `data/feishu_sync_payload.json`。

## 当前功能边界

该核心不会独立登录或实时抓取 Instagram。缺失播放量不会写成 0。

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
