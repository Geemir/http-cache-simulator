# ICS HTTP 缓存模拟器

[English](README.md)

这个 Python 命令行模拟器按时间顺序回放多个客户端的请求，模拟它们对同一 HTTP 缓存的访问。支持先进先出（FIFO）、最近最少使用（LRU）和最不常用（LFU）。LFU 访问次数相同时按 LRU 淘汰。程序以 JSON 输出整体及各客户端的性能指标。

## 快速开始

使用 Python 3.10 或更高版本，在仓库根目录运行以下命令。模拟器只使用 Python 标准库。

```shell
python -m cache_sim --resources examples/resources.csv --requests examples/requests.csv --capacity-bytes 10 --policy fifo
python -m unittest discover -s tests -v
```

样例请求轨迹含 7 次请求，其中 2 次命中，源站流量为 35 字节。命令行接口默认使用 102,400 字节（100 KiB）的缓存容量，命中延迟固定为 5 ms。缓存未命中时，响应时间取资源表中的源站获取延迟。大小超过缓存容量的资源直接由源站提供，缓存内容保持原样。

## 课程参考轨迹

把课程的 `resources.csv` 和 `requests_reference.csv` 放在仓库根目录。两个文件用 `scheme`、`host` 和 `path` 标识资源。模拟器将三列拼成 URL，用它查找资源，并按文件行的顺序处理请求。按课程的模拟设定，HTTP 状态码和 Cache-Control 等字段不影响结果。

```shell
python -m cache_sim --resources resources.csv --requests requests_reference.csv --policy lfu --events-csv lfu-events.csv
```

可用 `--policy fifo`、`--policy lru` 或 `--policy lfu` 选择规则。可选的事件 CSV 记录每条请求是否命中、移出的资源、按入缓存时间从早到晚排序的缓存内容、缓存占用（字节）、响应时间，以及累计源站流量和命中次数。淘汰资源和缓存内容两列使用 JSON 数组保存资源标识。

将课程的 `expected_fifo.csv`、`expected_lru.csv` 和 `expected_lfu.csv` 也放在根目录，运行测试便可逐条核对参考输出。

## 输入与输出

- 人工样例的两个 CSV 都使用 `resource_id` 代替三列 URL 字段。资源 CSV 需要 `size_bytes`（字节）和 `origin_latency_ms`（毫秒）。请求 CSV 需要 `client_id`（客户端标识）。读取器会忽略有列名的额外字段。
- JSON 中的 `overall` 汇总整条轨迹，`clients` 按客户端分别统计。两处使用相同的指标字段。

| JSON 字段 | 中文术语 | 计算方式或单位 |
| --- | --- | --- |
| `request_hit_ratio` | 请求命中率 | 缓存命中的请求数除以总请求数，输出 0 到 1 之间的比例 |
| `byte_hit_ratio` | 字节命中率 | 缓存提供的字节数除以请求的总字节数，输出 0 到 1 之间的比例 |
| `mean_response_ms` | 平均响应时间 | 各次请求的响应时间之和除以总请求数，单位为毫秒 |
| `origin_bytes` | 源站流量 | 缓存未命中时从源站获取的总字节数 |

[团队路线图（简体中文）](docs/roadmap.zh-CN.md)
