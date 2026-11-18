# ICS HTTP 缓存模拟器路线图

[English](roadmap.md)

本页日期和时间均为上海时间。Brightspace 提交截止时间为 **2026 年 12 月 4 日（周五）17:59**。团队计划于 **12 月 3 日 21:00** 前准备好最终 ZIP 和视频链接。

## 实现方案

模拟器是一个使用 Python 3.10 或更高版本的命令行程序。当前版本使用 Python 标准库。

| 路径 | 职责 |
| --- | --- |
| `cache_sim/models.py` | 定义资源、请求、缓存条目和指标等数据结构 |
| `cache_sim/io.py` | 将 CSV 数据转换为模拟器使用的记录 |
| `cache_sim/simulator.py` | 按顺序处理请求并计算性能指标 |
| `cache_sim/policies.py` | 定义缓存淘汰规则 |
| `cache_sim/__main__.py` | 提供命令行接口（CLI） |
| `tests/` | 保存测试用例 |
| `examples/` | 保存人工构造的 CSV 测试数据 |

命令行接口以 JSON 导出整体与各客户端的指标，供实验运行器统一收集。模拟器核心记录缓存占用、命中与未命中、条目访问计数，以及各请求对应的客户端。淘汰策略从现有缓存条目中选择要移除的资源。可选的事件回调可以按处理顺序记录命中、未命中和淘汰事件，以便核对参考输出。CSV 读取器按文件中的时间顺序处理各行。人工构造的样例采用 [中文 README](../README.zh-CN.md#输入与输出) 中的 CSV 格式。收到课程参考文件后，需逐项确认实际表头及单位。

参考验证从空缓存开始，容量为 102,400 字节（100 KiB）。命中延迟为 5 ms，未命中延迟取对应资源的源站获取延迟。超过缓存容量的资源直接由源站提供。每次评估都重新初始化为空缓存。对同一实验配置，各策略使用相同的请求轨迹、容量及其他参数。整体及各客户端均报告请求命中率、字节命中率、平均响应时间和源站流量，并保存原始测量结果、输入文件及复现命令。

## 分工与验收

| 负责人 | 日期 | 交付物 | 验收标准 |
| --- | --- | --- | --- |
| Oscar | 11 月 20 日 | 整理课程输入文件，并手算一条小型验证轨迹 | 在团队工作区共享两个 CSV 和参考输出，记录表头及单位，写出一条人工请求轨迹的预期事件与指标。 [#1](https://github.com/Geemir/http-cache-simulator/issues/1) |
| Alyx | 11 月 23 日 | 完成 FIFO、LRU 和 LFU | 用单元测试区分命中后各策略的淘汰行为，覆盖 LFU 访问次数相同的情形、多条目淘汰、超大资源不入缓存和资源恰好填满缓存。 [#2](https://github.com/Geemir/http-cache-simulator/issues/2) |
| Daniel | 11 月 23 日 | 接入课程 CSV 并导出逐请求事件 | 读取课程提供的文件，提供按顺序导出命中、未命中和淘汰事件的 CLI 命令，并验证新克隆的仓库可以运行。 [#3](https://github.com/Geemir/http-cache-simulator/issues/3) |
| Ryan | 11 月 23 日 | 确定自定义策略与实验方案 | 在查看最终结果前，说明优化目标、缓存准入和淘汰规则、并列判定规则、实验假设，以及负载与容量取值。 [#4](https://github.com/Geemir/http-cache-simulator/issues/4) |
| Alyx | 11 月 25 日 | 对照课程输出验证三种基线策略 | 核对已发布的全部指标及可用的事件明细，记录差异和处理结果，保留可重复执行的验证命令。 [#5](https://github.com/Geemir/http-cache-simulator/issues/5) |
| Oscar | 11 月 25 日 | 准备三类可复现的工作负载轨迹 | 按 Ryan 的实验设计构造重复访问、顺序访问和混合负载，记录访问模式、客户端标识，并在使用随机生成时记录随机种子。 [#6](https://github.com/Geemir/http-cache-simulator/issues/6) |
| Daniel | 11 月 27 日 | 自动运行策略、负载与容量的组合 | 每组实验从空缓存开始，稳定导出机器可读的整体及分客户端指标，记录一条复现命令。 [#7](https://github.com/Geemir/http-cache-simulator/issues/7) |
| Ryan | 11 月 27 日 | 实现并测试自定义策略 | 让 CLI 可以选择该策略，测试评分与并列判定规则，并用一条针对性的人工轨迹验证预期行为。 [#8](https://github.com/Geemir/http-cache-simulator/issues/8) |
| Ryan | 11 月 29 日 | 运行实验并整理结果、图表和报告分析 | 保存原始数据。解释策略表现如何随负载与容量变化、指标之间有何取舍，以及各客户端受到的影响。 [#9](https://github.com/Geemir/http-cache-simulator/issues/9) |
| Alyx | 12 月 1 日 | 复核实验正确性并撰写报告相关章节 | 独立复算并抽查指标与策略行为，撰写模拟器、数据结构和参考验证章节。 [#10](https://github.com/Geemir/http-cache-simulator/issues/10) |
| Oscar | 12 月 2 日 | 编写 HOWTO、从新克隆或解压的副本验证流程，并协调录制 | 让一名队友按 HOWTO 复现一次运行。协调 12 分钟的演示脚本，每位组员讲解 3 分钟，并安排可复现的 CLI 演示。 [#11](https://github.com/Geemir/http-cache-simulator/issues/11) |
| Daniel | 12 月 3 日 | 整合 3–4 页技术报告并验证提交包 | 从 ZIP 解压后运行验证，核对输入、输出、说明和报告是否齐全，并在 Brightspace 提交前验证 YouTube 链接。 [#12](https://github.com/Geemir/http-cache-simulator/issues/12) |

## 里程碑

- **11 月 23 日 21:00** — 三种标准策略、课程 CSV 读取流程和自定义策略方案就绪。Daniel 检查集成，Alyx 和 Ryan 一起核对模拟假设。 [M1](https://github.com/Geemir/http-cache-simulator/milestone/1)
- **11 月 29 日 21:00** — 完成基线验证、自定义策略测试和实验矩阵，产出初版图表。Ryan 和 Oscar 核对负载轨迹，Alyx 抽查结果。 [M2](https://github.com/Geemir/http-cache-simulator/milestone/2)
- **12 月 3 日 21:00** — 审阅报告和 ZIP，完成四位成员的录制并验证视频链接。Daniel 和 Oscar 一起检查实际提交文件。 [M3](https://github.com/Geemir/http-cache-simulator/milestone/3)

负载准备与自定义策略设计可和基线开发并行。正式结论以完整的参考运行及经核验的官方指标为基础。每位成员查看自己任务所依赖的 issue，并在视频中说明自己的贡献。
