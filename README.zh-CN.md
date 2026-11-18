# ICS HTTP 缓存模拟器

[English](README.md)

这个 Python 命令行模拟器按时间顺序回放多个客户端的请求，模拟它们对同一 HTTP 缓存的访问。当前版本实现了先进先出（FIFO）淘汰策略，按字节计算缓存占用，并以 JSON 输出整体及各客户端的性能指标。

## 快速开始

使用 Python 3.10 或更高版本，在仓库根目录运行以下命令。当前版本仅使用 Python 标准库。

```shell
python -m cache_sim --resources examples/resources.csv --requests examples/requests.csv --capacity-bytes 10 --policy fifo
python -m unittest discover -s tests -v
```

样例请求轨迹含 7 次请求，其中 2 次命中，源站流量为 35 字节。命令行接口默认使用 102,400 字节（100 KiB）的缓存容量，命中延迟固定为 5 ms。缓存未命中时，响应时间取资源表中的源站获取延迟。大小超过缓存容量的资源直接由源站提供，缓存内容保持原样。

## 输入与输出

- 资源元数据 CSV 的表头为 `resource_id,size_bytes,origin_latency_ms`，分别表示资源标识、大小（字节）和源站获取延迟（毫秒）。
- 请求轨迹 CSV 的表头为 `client_id,resource_id`，分别表示客户端标识和所请求的资源标识。按时间顺序排列各行。读取器会忽略有列名的额外字段。
- JSON 中的 `overall` 汇总整条轨迹，`clients` 按客户端分别统计。两处使用相同的指标字段。

| JSON 字段 | 中文术语 | 计算方式或单位 |
| --- | --- | --- |
| `request_hit_ratio` | 请求命中率 | 缓存命中的请求数除以总请求数，输出 0 到 1 之间的比例 |
| `byte_hit_ratio` | 字节命中率 | 缓存提供的字节数除以请求的总字节数，输出 0 到 1 之间的比例 |
| `mean_response_ms` | 平均响应时间 | 各次请求的响应时间之和除以总请求数，单位为毫秒 |
| `origin_bytes` | 源站流量 | 缓存未命中时从源站获取的总字节数 |

样例 CSV 是人工构造的测试数据。课程提供的 CSV 格式与参考输出有待核验。 [团队路线图（简体中文）](docs/roadmap.zh-CN.md)
