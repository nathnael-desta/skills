# Research prompt: what an offline transit router can precompute

## Context (read carefully; do not assume a normal timetable network)

We build an offline public-transport journey planner for Addis Ababa that runs entirely on the phone (React Native, Hermes JavaScript engine, no JIT in Expo Go). Data ships as a "pack" compiled offline on a server and downloaded once.

Network: about 2,270 boarding places (stops), 891 line patterns (a route in one direction), 447 routes. Vehicle types: minibus taxis (12 seats, about 250 lines), midibuses (25 seats), city buses (Anbessa, Sheger) and 2 light-rail lines.

What makes it unusual:
1. **No timetables.** Lines run by frequency only (minibuses leave when full). Waits are estimates per line and time-of-day slot.
2. **Board only at boarding places, get off anywhere.** Riders may drop off at any point along a line, not just at stops.
3. **Per-rider weights.** Each rider sets 1-5 "how much do you mind" scores (walking, waiting, paying, changing vehicles, vehicle types). These become weights in one generalized cost ("minutes of effort"), so weights change per query.
4. **Fares:** minibus and midibus fares are by distance band; bus fares are flat per line, set by the line's length.

Current engine: RAPTOR variant that keeps ONE effort number per stop per round (round k = reached with exactly k rides), stored in flat typed arrays. Measured on a Samsung Galaxy A55 in Expo Go: two searches per tap (one for "Fastest/Fewest transfers", one for "Lowest cost") take 59 ms median, 98 ms at the 95th percentile, over 166 test trips. The previous five-criteria McRAPTOR took 606 ms median. The slowest supported phone (OnePlus Nord N100) is about 2.6x slower than the A55.

Known weakness: the one-number search returns only 2-3 distinct route options per query (the old one returned 5).

## Questions

1. **Precomputation in the pack.** For each candidate below: does it stay correct with frequency-only lines, drop-off anywhere and per-query weights? What does the literature report for speed-up and storage? What would it cost in pack size for our network size? Is there an open-source implementation (with its licence)?
   - Per line, the best drop-off point near each boarding place within walking reach (ULTRA-style transfer shortcuts).
   - Lower-bound tables from 16-32 landmark stops (ALT), scaled by the rider's weights at query time, to prune the search.
   - Cumulative ride-time and fare arrays per line and time slot.
   - Shipping the search's arrays in a ready-to-load binary layout instead of JSON.
   - A spatial index for snapping origin and destination to nearby lines.
   - Anything else you find that fits these constraints.
2. **Hybrids of methods usually ruled out for us.**
   - Transfer Patterns computed over a *range* of weights (every line sequence that is optimal for some weight combination in a bounded box), so the phone only scores a few stored sequences with the rider's own weights. Has anyone published this (multi-criteria or "weight-robust" transfer patterns, Pareto sets over weight ranges)? What are the storage and correctness results?
   - Generating synthetic timetables from frequencies (as Digital Matatus and Trufi did) to use Connection Scan or Trip-Based routing. What is lost?
   - Spiess & Florian hyperpath / optimal-strategy scans: query speed against RAPTOR, and what they return.
3. **Diverse alternatives cheaply.** Methods to return 4-5 genuinely different route options (different line sequences) from a scalar-label RAPTOR: k-best labels per stop, penalty/exclusion reruns, plateau methods, route-diversity heuristics. Cost of each.

## Rules for the answer

- Mark every number as **measured** (and where: paper, table, network) or **projected**. Never put projections in a column of measured numbers.
- List every source as **opened in full** or **snippet only**.
- Say plainly when something could not be verified.
- End with a ranked list: what to try first on our data, and why.
