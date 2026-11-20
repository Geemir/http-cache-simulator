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

Oscar 提供的六份课程文件已在仓库根目录。资源表 `resources.csv` 用 `scheme`、`host`、`path` 标识 URL，`size_bytes` 表示字节数，`origin_latency_ms` 表示源站延迟（毫秒）。请求表 `requests_reference.csv` 使用相同的 URL 三列，另有 `timestamp`、`client_id`、`method`。三个客户端的 15 次 GET 已按时间先后排列，程序按 CSV 行序回放。课程设定忽略 HTTP 状态码和 Cache-Control。

```shell
mkdir -p results
for policy in fifo lru lfu; do
  python -m cache_sim --resources resources.csv --requests requests_reference.csv \
    --capacity-bytes 102400 --hit-latency-ms 5 --policy "$policy" \
    --events-csv "results/$policy-events.csv" > "results/$policy-summary.json"
done
python -m unittest discover -s tests -p test_reference.py -v
```

可用 `--policy fifo`、`--policy lru` 或 `--policy lfu` 选择规则。可选的事件 CSV 记录每条请求是否命中、移出的资源、按入缓存时间从早到晚排序的缓存内容、缓存占用（字节）、响应时间，以及累计源站流量和命中次数。淘汰资源和缓存内容两列使用 JSON 数组保存资源标识。

最后一条命令会把日志中的 URL 映射为答案里的 A–E，将参考占用量从 KiB 换算成字节（1 KiB = 1,024 字节），并逐行核对三份 `expected_*.csv`。打开 JSON 的 `overall` 可快速复核：FIFO、LRU、LFU 分别命中 3、3、4 次，源站流量分别为 421,888、403,456、370,688 字节。

## Oscar 的 10 次请求演示

```shell
python -m cache_sim --resources examples/oscar/demo/resources.csv \
  --requests examples/oscar/demo/requests.csv --capacity-bytes 102400 \
  --hit-latency-ms 5 --policy fifo --events-csv oscar-fifo-events.csv
```

将策略改为 `lru` 或 `lfu`，比较第 7 步的淘汰对象。FIFO 淘汰 A，LRU 淘汰 B，LFU 淘汰 C。第 8 步请求的资源为 120 KiB，三种策略均回源，缓存内容保持原样。[Oscar 的逐步手算表](docs/oscar_hand_calculation.md)

## 输入与输出

### 批量运行实验

```shell
python -m cache_sim.batch --plan examples/batch-plan.json --output results/sample-matrix.csv
```

样例用 README 和 Oscar 的两份轨迹，各跑 10 字节和 102,400 字节两档容量。以现有三种策略计算，共运行 12 次，每次从空缓存开始，合计输出 36 行数据。筛选 `scope=overall` 可看各组整体结果，筛选 `scope=client` 可按客户端比较。每行保留工作负载、策略、容量、命中延迟，以及单次运行 JSON 的全部统计值，保留原始精度。[样例结果表](results/sample-matrix.csv)

正式实验时，将[样例计划](examples/batch-plan.json)复制为 `experiments/plan.json`，把容量改为 Ryan 确定的字节数，在 `workloads` 中填入 Oscar 的重复、顺序、混合三组 CSV 路径。输入路径相对于计划文件解析。命令会运行 `cache_sim.policies.POLICIES` 中的所有策略，第四种策略注册后会自动纳入。将正式计划与输入一并保存，在仓库根目录运行：

```shell
python -m cache_sim.batch --plan experiments/plan.json --output results/matrix.csv
```

### 单次运行的字段

- 人工样例的两个 CSV 都使用 `resource_id` 代替三列 URL 字段。资源 CSV 需要 `size_bytes`（字节）和 `origin_latency_ms`（毫秒）。请求 CSV 需要 `client_id`（客户端标识）。读取器会忽略有列名的额外字段。
- JSON 中的 `overall` 汇总整条轨迹，`clients` 按客户端分别统计。两处使用相同的指标字段。

| JSON 字段 | 中文术语 | 计算方式或单位 |
| --- | --- | --- |
| `request_hit_ratio` | 请求命中率 | 缓存命中的请求数除以总请求数，输出 0 到 1 之间的比例 |
| `byte_hit_ratio` | 字节命中率 | 缓存提供的字节数除以请求的总字节数，输出 0 到 1 之间的比例 |
| `mean_response_ms` | 平均响应时间 | 各次请求的响应时间之和除以总请求数，单位为毫秒 |
| `origin_bytes` | 源站流量 | 缓存未命中时从源站获取的总字节数 |

[团队路线图（简体中文）](docs/roadmap.zh-CN.md)
