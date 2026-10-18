# FPL Empirical Strength Normalization and Blending

## Context
Solio team strength exports provide prior attack and defense ratings (`Goals`, `Goals Conceded`). To reflect on-pitch reality during the Premier League season without overfitting early-season schedule variations, we need an objective, verifiable calibration model.

## Decision
1. **FPL Empirical Form**: For each finished match, combine actual goals and expected goals with equal weight: $0.5 \times G + 0.5 \times xG$ for attack, and $0.5 \times GC + 0.5 \times xGC$ for defense.
2. **Leave-One-Out Opponent Normalization**: Adjust match performance against opponent defensive and attacking strength across all other matches in the season. Smooth opponent ratings toward league average with $M=3$ Bayesian pseudo-matches and clamp the difficulty multiplier between $[0.65, 1.35]$.
3. **Pre-season and Zero-Match Invariant**: When no gameweeks have finished (or a team has 0 finished matches), fall back entirely to Base Strength ($\lambda = 0.0$).
4. **Adaptive Season Progression & Team-Specific Blend Weight**: Support automated blend weight progression based on completed matches played per team ($n_i$) alongside manual override (`--weight`). Linear progression scales Solio baseline from 100% at 0 matches ($w_i=0.0$) to 0% at 19 matches ($w_i=1.0$), with 19+ matches operating on 100% empirical season stats ($w_i = \min(n_i / 19.0, 1.0)$). When teams have differing numbers of matches played (due to provisional fixtures, postponements, or blank/double gameweeks), each team receives an individualized Team-Specific Blend Weight proportional to its own empirical sample size. Manual `--weight` remains a uniform override across all teams with $n_i \ge 1$.

