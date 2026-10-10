# FPL Empirical Strength Normalization and Blending

## Context
Solio team strength exports provide prior attack and defense ratings (`Goals`, `Goals Conceded`). To reflect on-pitch reality during the Premier League season without overfitting early-season schedule variations, we need an objective, verifiable calibration model.

## Decision
1. **FPL Empirical Form**: For each finished match, combine actual goals and expected goals with equal weight: $0.5 \times G + 0.5 \times xG$ for attack, and $0.5 \times GC + 0.5 \times xGC$ for defense.
2. **Leave-One-Out Opponent Normalization**: Adjust match performance against opponent defensive and attacking strength across all other matches in the season. Smooth opponent ratings toward league average with $M=3$ Bayesian pseudo-matches and clamp the difficulty multiplier between $[0.65, 1.35]$.
3. **Pre-season and Zero-Match Invariant**: When no gameweeks have finished (or a team has 0 finished matches), fall back entirely to Base Strength ($\lambda = 0.0$).
4. **Adaptive Season Progression**: Support automated blend weight progression based on completed gameweeks alongside manual override (`--weight`). Linear progression decays Solio baseline from 100% at GW 0 ($w=0.0$) to 0% at GW 19 finished ($w=1.0$), with GW 20 onward operating on 100% empirical season stats.
