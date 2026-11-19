# ICS HTTP 缓存模拟器路线图

[English](roadmap.md)

**时间（均为上海时间）** — **2026 年 12 月 3 日 21:00** 前准备好 ZIP 和视频链接。Brightspace 正式截止时间是 **12 月 4 日（周五）17:59**。

程序按顺序读取一份文件请求列表，也叫请求轨迹。缓存里已经有该文件，就算一次**命中**。找不到就是**未命中**，程序会计算从原本提供文件的服务器（源站）下载所需的时间和字节数。缓存放不下新文件时，由缓存规则决定先移出谁。我们用同样的请求列表测试四种规则，比较各自的表现。

## 每个人要做什么

### Oscar · 找课程文件、准备请求列表、组织演示

1. **11 月 20 日** — 先去 Brightspace 找两个课程 CSV 和老师给的参考输出，发给 Daniel 和 Alyx。用表格做一个短例子，手算应该得到什么结果。 [#1](https://github.com/Geemir/http-cache-simulator/issues/1)
2. **11 月 25 日** — 按 Ryan 给的要求，做三份请求列表，分别模拟重复访问、顺序访问和混合访问。把列表、对应的资源表和制作方法交给 Ryan。 [#6](https://github.com/Geemir/http-cache-simulator/issues/6)
3. **12 月 2 日** — 写一份可以照着做的运行说明，请一名队友试跑。组织 12 分钟录制，每人讲 3 分钟，最后检查 YouTube 链接能打开。 [#11](https://github.com/Geemir/http-cache-simulator/issues/11)

### Alyx · 完成三种标准规则并检查结果

1. **11 月 23 日** — 先看已有的 FIFO 代码。让三种标准规则都能运行，用短测试证明每种规则会移出哪个文件。 [#2](https://github.com/Geemir/http-cache-simulator/issues/2)
2. **11 月 25 日** — Oscar 共享参考文件、Daniel 跑通课程输入后，用三种标准规则各跑一次。交一份老师的预期值与程序实际结果的对照表，附上可以重跑的命令。 [#5](https://github.com/Geemir/http-cache-simulator/issues/5)
3. **12 月 1 日** — 抽查 Ryan 的几组结果，写清程序怎么工作、团队怎么核对结果，把报告草稿交给 Daniel。 [#10](https://github.com/Geemir/http-cache-simulator/issues/10)

### Ryan · 设计新规则并解释实验结果

1. **11 月 23 日** — 先选你想改善的指标，比如响应时间或源站流量。写下新规则怎么工作、实验用哪些请求列表和缓存大小。把访问模式交给 Oscar，把要跑的组合交给 Daniel。 [#4](https://github.com/Geemir/http-cache-simulator/issues/4)
2. **11 月 27 日** — 把规则写进程序，用短请求列表验证实际行为。 [#8](https://github.com/Geemir/http-cache-simulator/issues/8)
3. **11 月 29 日** — 用 Oscar 的输入文件和 Daniel 的批量命令跑四种规则。保存结果和图，解释每种规则在什么情况下比较好、不同客户端受到什么影响。把结果交给 Alyx 核对，把分析交给 Daniel。 [#9](https://github.com/Geemir/http-cache-simulator/issues/9)

### Daniel · 让程序易于运行并整理提交材料

1. **11 月 23 日** — 先跑 README 的样例。收到 Oscar 的课程文件后，让程序能读这些文件，并加一个选项，把每条请求中发生的事写进日志。把运行命令交给 Alyx。 [#3](https://github.com/Geemir/http-cache-simulator/issues/3)
2. **11 月 27 日** — 做一个命令，一次跑完计划里的实验并生成结果表。用样例试跑后，把命令交给 Ryan。 [#7](https://github.com/Geemir/http-cache-simulator/issues/7)
3. **12 月 3 日** — 把各部分整合成 3–4 页报告，按要求打包 ZIP，并解压到新目录试跑。和 Oscar 一起核对最终 ZIP 和视频链接。 [#12](https://github.com/Geemir/http-cache-simulator/issues/12)

## 团队检查点

- **11 月 23 日 21:00** — 三种标准规则能跑，程序能读取课程文件，新规则的设计已写清楚。 [M1](https://github.com/Geemir/http-cache-simulator/milestone/1)
- **11 月 29 日 21:00** — 已核对课程参考结果，四种规则已按计划的请求列表和缓存大小跑完，初版图表就绪。 [M2](https://github.com/Geemir/http-cache-simulator/milestone/2)
- **12 月 3 日 21:00** — 报告和 ZIP 已检查，四人均完成录制，视频链接可打开。 [M3](https://github.com/Geemir/http-cache-simulator/milestone/3)

## 写代码和跑实验时查这里

- 使用 Python 3.10 或以上版本。现有代码只用标准库。`cache_sim/models.py` 定义数据，`cache_sim/io.py` 读取 CSV，`cache_sim/simulator.py` 处理请求，`cache_sim/policies.py` 保存缓存规则，`cache_sim/__main__.py` 负责运行命令。测试在 `tests/`，样例 CSV 在 `examples/`。 [运行样例](../README.zh-CN.md#快速开始)
- 程序按文件行的顺序处理请求。接入课程 CSV 前，先核对表头和单位。模拟器可以按顺序记录命中、未命中和移出哪些文件，并以 JSON 输出整体和每个客户端的统计。
- 核对老师的参考结果时，从 **102,400 字节**的空缓存开始。命中按 **5 ms** 计算，未命中按资源表里的源站获取时间计算。比整个缓存还大的文件不放入缓存。
- 正式实验每次都从空缓存开始。所有规则用同样的请求列表和缓存大小。保存输入、运行命令和原始结果。整体和每个客户端都统计请求命中率、字节命中率、平均响应时间和源站流量。
