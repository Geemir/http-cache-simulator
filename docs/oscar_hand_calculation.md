# Hand calculation for a 10-request trace

Use `examples/oscar/demo/resources.csv` and `examples/oscar/demo/requests.csv`. The shared cache starts empty, holds **100 KiB (102,400 bytes)** and serves hits in **5 ms**. A miss uses the origin latency shown below and contributes the full resource size to origin traffic.

| Resource | Size (KiB) | Origin latency (ms) |
| --- | ---: | ---: |
| A | 30 | 100 |
| B | 35 | 150 |
| C | 25 | 60 |
| D | 30 | 90 |
| E | 120 | 350 |

## Request-by-request results

Each cell gives **result and time / eviction / cache contents after the request**. Cache contents are listed in insertion order. A dash means no eviction. On every miss, add the requested resource’s size to origin traffic.

| Step | Client | Resource | FIFO | LRU | LFU |
| ---: | --- | --- | --- | --- | --- |
| 1 | alice | A | M 100 / – / A | M 100 / – / A | M 100 / – / A |
| 2 | ben | B | M 150 / – / A B | M 150 / – / A B | M 150 / – / A B |
| 3 | alice | B | H 5 / – / A B | H 5 / – / A B | H 5 / – / A B |
| 4 | ben | B | H 5 / – / A B | H 5 / – / A B | H 5 / – / A B |
| 5 | ben | A | H 5 / – / A B | H 5 / – / A B | H 5 / – / A B |
| 6 | alice | C | M 60 / – / A B C | M 60 / – / A B C | M 60 / – / A B C |
| 7 | ben | D | M 90 / A / B C D | M 90 / B / A C D | M 90 / C / A B D |
| 8 | alice | E | M 350 / – / B C D | M 350 / – / A C D | M 350 / – / A B D |
| 9 | ben | C | H 5 / – / B C D | H 5 / – / A C D | M 60 / D / A B C |
| 10 | alice | B | H 5 / – / B C D | M 150 / A / C D B | H 5 / – / A B C |

At step 3, Alice hits B after Ben downloaded it. At step 7, A entered the cache first, B’s last access was earliest (step 4), and C had the lowest frequency (one access). That is why FIFO evicts A, LRU evicts B and LFU evicts C. At step 8, E costs 120 KiB of origin traffic and 350 ms. Its 120 KiB size exceeds the cache capacity, so nothing is evicted and E stays out of the cache.

## Manual totals

Total demand is `2 × 30 + 4 × 35 + 2 × 25 + 30 + 120 = 400 KiB`. Common misses at steps 1, 2, 6, 7 and 8 cost `30 + 35 + 25 + 30 + 120 = 240 KiB`. LRU adds the B miss at step 10 and LFU adds the C miss at step 9.

| Metric | FIFO | LRU | LFU |
| --- | ---: | ---: | ---: |
| Request hit ratio | 5/10 = 50% | 4/10 = 40% | 4/10 = 40% |
| Byte hit ratio | 160/400 = 40% | 125/400 = 31.25% | 135/400 = 33.75% |
| Origin traffic | 245,760 B | 281,600 B | 271,360 B |
| Mean response time | 775/10 = 77.5 ms | (775 + 145)/10 = 92 ms | (775 + 55)/10 = 83 ms |

The FIFO sum is `100 + 150 + 5 + 5 + 5 + 60 + 90 + 350 + 5 + 5 = 775 ms`. Compared with FIFO, a miss for B adds `150 − 5 = 145 ms` under LRU, and a miss for C adds `60 − 5 = 55 ms` under LFU. LRU and LFU therefore have the same request hit ratio here and different byte hit ratios and response times.

| Policy | Client | Request hit ratio | Byte hit ratio | Mean response | Origin traffic |
| --- | --- | ---: | ---: | ---: | ---: |
| FIFO | alice | 2/5 | 70/245 | 104 ms | 179,200 B |
| FIFO | ben | 3/5 | 90/155 | 51 ms | 66,560 B |
| LRU | alice | 1/5 | 35/245 | 133 ms | 215,040 B |
| LRU | ben | 3/5 | 90/155 | 51 ms | 66,560 B |
| LFU | alice | 2/5 | 70/245 | 104 ms | 179,200 B |
| LFU | ben | 2/5 | 65/155 | 62 ms | 92,160 B |

All three policies were run with these CSVs. Their results match the table. See [replay commands](../README.md#oscars-10-request-demo) for the commands.
