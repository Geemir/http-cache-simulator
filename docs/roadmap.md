# ICS HTTP Cache Simulator Roadmap

[简体中文](roadmap.zh-CN.md)

**Timeline (Shanghai time)** — Have the ZIP and video link ready by **December 3, 2026 at 21:00**. The Brightspace deadline is **Friday, December 4 at 17:59**.

The program reads a list of file requests in order. It checks whether each file is already in the shared cache. Finding it is a *hit*. Otherwise it is a *miss*, and the program counts the time and bytes needed to download it from the original server. If a new file needs room, the chosen cache rule decides what to remove. We will run the same request lists under four cache rules and compare the results.

## Who does what

### Oscar · Find the course files, prepare request lists, and organize the demo

1. **Nov 20** — Start in Brightspace. Share the two course CSVs and the teacher’s expected results with Daniel and Alyx. Make a short example in a spreadsheet and calculate its expected results by hand. [#1](https://github.com/Geemir/http-cache-simulator/issues/1)
2. **Nov 25** — Use Ryan’s plan to make three request lists: repeated, sequential, and mixed. Give Ryan the lists, their matching resource tables, and notes on how to make them again. [#6](https://github.com/Geemir/http-cache-simulator/issues/6)
3. **Dec 2** — Write steps someone can follow to run the program, and ask a teammate to try them. Organize the 12-minute recording with three minutes per person and check the YouTube link. [#11](https://github.com/Geemir/http-cache-simulator/issues/11)

### Alyx · Finish and check the cache rules

1. **Nov 23** — Start with the FIFO code. Get the three standard rules working and write short tests that show which files each one removes. [#2](https://github.com/Geemir/http-cache-simulator/issues/2)
2. **Nov 25** — Once Oscar shares the reference files and Daniel gets the course input working, run the three standard rules. Share a table of expected and actual results and the command to repeat the check. [#5](https://github.com/Geemir/http-cache-simulator/issues/5)
3. **Dec 1** — Check a few of Ryan’s results and write the report sections on how the program works and how the team checked its results. Send the draft to Daniel. [#10](https://github.com/Geemir/http-cache-simulator/issues/10)

### Ryan · Design our rule and explain what the experiments show

1. **Nov 23** — Start by choosing what to improve, such as response time or traffic. Write down how the new rule works and which inputs and cache sizes to test. Give Oscar the request patterns and Daniel the planned combinations. [#4](https://github.com/Geemir/http-cache-simulator/issues/4)
2. **Nov 27** — Add the new rule to the program. Test it on a short request list that shows what it does. [#8](https://github.com/Geemir/http-cache-simulator/issues/8)
3. **Nov 29** — Use Oscar’s inputs and Daniel’s batch command to test all four rules. Save the results and charts. Explain when each rule does well and how it affects different clients. Share the results with Alyx and the write-up with Daniel. [#9](https://github.com/Geemir/http-cache-simulator/issues/9)

### Daniel · Make the program easy to run and assemble the submission

1. **Nov 23** — Start with the example command in the README. Once Oscar shares the course files, make the program read them and add an option to write a log of what happened for each request. Give Alyx the command to run it. [#3](https://github.com/Geemir/http-cache-simulator/issues/3)
2. **Nov 27** — Make one command to run all the requested experiments and produce a result table. Try it on the starter example and give Ryan the command. [#7](https://github.com/Geemir/http-cache-simulator/issues/7)
3. **Dec 3** — Combine the report sections into 3–4 pages, put the deliverables in a ZIP, and test it after extracting it to a new folder. Check the final ZIP and video link with Oscar. [#12](https://github.com/Geemir/http-cache-simulator/issues/12)

## Team checkpoints

- **Nov 23 at 21:00** — The three standard rules work, the program reads the course files, and the team has a written plan for the new rule. [M1](https://github.com/Geemir/http-cache-simulator/milestone/1)
- **Nov 29 at 21:00** — The course results have been checked, the four rules have been tested on the planned inputs and cache sizes, and the first charts are ready. [M2](https://github.com/Geemir/http-cache-simulator/milestone/2)
- **Dec 3 at 21:00** — The report and ZIP have been checked, all four people have recorded their segments, and the video link works. [M3](https://github.com/Geemir/http-cache-simulator/milestone/3)

## Reference for coding and experiments

- Use Python 3.10 or newer. The starter uses the standard library. `cache_sim/models.py` defines the data, `cache_sim/io.py` reads CSVs, `cache_sim/simulator.py` processes requests, `cache_sim/policies.py` contains the cache rules, and `cache_sim/__main__.py` handles the terminal command. Tests are in `tests/` and sample CSVs are in `examples/`. [Run the example](../README.md#quick-start)
- The CSV reader works in file order. Confirm the course column names and units before adapting the reader. The simulator can record hits, misses, and removals in order. It provides overall and per-client summaries in JSON.
- When checking the teacher’s results, start with an empty **102,400-byte** cache and use **5 ms** for a hit. Use the time in the resource table for a miss. If a file is bigger than the whole cache, leave it out.
- In the full experiment, start each run with an empty cache. Give all rules the same request lists and cache sizes. Save the inputs, commands, and raw results. Report request hit rate, byte hit rate, average response time, and server traffic for the whole run and for each client.
