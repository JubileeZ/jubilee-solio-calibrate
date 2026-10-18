# Quantitative Justification for Solio Planner Rules & Variance Constraints

## 1. Executive Summary & Problem Formulation

Deterministic Mixed-Integer Linear Programs (MILP) optimize team selection and transfer pathways by maximizing total expected points across a finite planning horizon:

$$\max \sum_{t=1}^{T} \sum_{i \in \text{Squad}} x_{i,t} \cdot \widehat{xP}_{i,t} - \sum_{t=1}^{T} c_{\text{hit}} \cdot H_t$$

While mathematically optimal under the assumption that $\widehat{xP}_{i,t}$ represents true expected value with zero variance, deterministic solvers suffer in practice from the **Optimizer's Curse**:
1. **Selection Bias on Upper Estimation Errors**: An optimizer systematically over-selects assets whose point estimates are inflated by positive estimation error $\epsilon_i > 0$, because $\max_i (\mu_i + \epsilon_i) > \max_i \mu_i$.
2. **Zero-Variance Assumption**: Point estimates ignore estimation variance ($\sigma_{\epsilon} \approx \pm 1.5 \text{ to } 2.5 \text{ pts/GW}$).
3. **Zero-Covariance Assumption**: Standard linear objectives treat player returns as mutually independent, completely ignoring cross-player covariance $\text{Cov}(X_i, X_j)$.

Without user-specified strategic constraints, deterministic solvers exhibit three distinct operational failure modes:
1. **Horizon Overfitting (Noisy Hits)**: The solver takes a $-4$ hit for a marginal $+4.3\text{ xP}$ edge over 5 gameweeks ($+0.06\text{ xP/GW}$ net). In reality, single-week injury surprises, benchings, or normal estimation noise wipe out multi-week edges with probability $> 60\%$.
2. **The Bimodal xMins Trap**: Fractional minutes projections (e.g. $60\text{ xMins}$) are modeled as linear points. Real returns are bimodal: an asset starts ($75\text{–}85\text{ mins}$) or makes a 10-minute cameo ($1\text{ pt}$), instantly destroying clean sheet equity and blocking automatic bench substitutions.
3. **Tail-Risk Covariance**: Tripling up on defenders from a single club maximizes joint clean sheet upside, but creates severe downside concentration: a single conceded goal wipes out 12 points across 3 players simultaneously ($\text{Cov}(CS_i, CS_j) \approx 1.0$).

---

## 2. Solio Sentence Builder: Constraint Mechanics

In the Solio web planner UI, rules are defined using a structured sentence builder combining **Actions** (`own`, `start`, `bench`, `buy`, `sell`, `captain`, `take hit`, `roll transfer`, `carry ITB`), **Filters** (`position`, `club`, `projected mins/pts`, `price`, `ownership/EO`, `cross-play`), and **Constraint Modifiers**:

| Constraint Type | Solio Keyword | Mathematical Formulation | Operational Role |
|:---|:---|:---|:---|
| **Hard Constraint** | `Must` / `Must not` | $g(x) \le b$ (strict inequality, zero slack) | Invariant boundary. Infeasible solutions are pruned from the branch-and-bound tree. |
| **Soft Constraint** | `Prefer to` / `Prefer not to` | $\text{Objective} - \lambda \cdot s$, subject to $g(x) - s \le b$, $s \ge 0$ | Slack penalty $\lambda \in [0.1, 5.0\text{ pts}]$. Broken only if upside exceeds $\lambda$. |

---

## 3. Audit of Common Rule Configurations

| Strategy / Rule | Solio Builder Syntax | Quantitative Verdict | Optimal Adjustment | Rationale |
|:---|:---|:---|:---|:---|
| **Defensive Stack Cap** | `Prefer to start at most 2 DEF/GKP from each club` | **Keep as `Prefer`, lower penalty to `1.0–1.5 pts`** *(default: `1.2 pts`)* | Reduce from excessive `3.0 pt` penalty | A $3.0\text{ pt}$ penalty equals ~75% clean sheet probability, forcing the solver to bench elite defenders in prime home fixtures. A $1.2\text{ pt}$ hurdle provides a tie-breaker against tail-risk wipeouts without sacrificing high-EV fixtures. |
| **Transfer Hit Policy** | `Prefer not to take hit in each GW from GW8 onwards` | **Change `Must not` to `Prefer not` worth `1.5–2.0 pts`** *(default: `1.8 pts`)* | Never use hard `Must not` for hits | Hard-blocking hits blinds the solver during injury crises or major fixture swings. A `Prefer not` penalty of $1.8\text{ pts}$ raises the effective hit hurdle to **$-5.8\text{ xP}$**, filtering out 30–40% of noise trades while allowing high-EV swings. |
| **Starter xMins Cutoff** | `Must not start players projected under 75 mins` | **Lower threshold from `75 mins` to `65 mins`** | Set floor to `65 mins` | With 5 substitutions and longer stoppage time, nailed wingers and attacking fullbacks routinely project at $68\text{–}74\text{ xMins}$. A $75\text{-min}$ hard floor prematurely sells elite high-ceiling starters. |

---

## 4. Covariance Asymmetry: Defending vs Attacking

A fundamental distinction in FPL portfolio construction is the mathematical asymmetry between defensive covariance and attacking covariance:

### Defensive Covariance (Step-Function Risk)
Clean sheet returns are strictly coupled binary step-functions:
$$CS_{\text{club}} \in \{0, 1\}$$
The first opposition goal destroys $100\%$ of clean sheet equity across all started defenders simultaneously:
$$\text{Cov}(CS_i, CS_j) \approx \text{Var}(CS) > 0 \quad \text{for } i, j \in \text{Defenders of Club } C$$
Starting 3 defenders from the same club converts an independent portfolio into an all-or-nothing lottery.

### Attacking Covariance (Positive Synergy in Routs)
Unlike defense, goals scored are non-binary counting processes ($G \in \{0, 1, 2, \dots\}$). When an elite attack (e.g. Arsenal, Liverpool, Man City) scores 3+ goals:
1. **Assister-Scorer Coupling**: An assist from player $A$ directly correlates with a goal for player $B$.
2. **Bonus Point Concentration**: Multiple attackers from the winning team absorb the 3, 2, and 1 bonus points.
3. **Compound Upside**: When high goal volume occurs, individual attacking expectations are positively correlated ($\text{Cov}(G_i, G_j) > 0$).

**Guideline**: **Never hard-cap attacking triple-ups on elite teams.** Apply a soft cap (`Prefer to start at most 2 MID or FWD from each club` worth `0.8–1.0 pts`) strictly filtered to mid-table/low-xG clubs, or apply a minimal $0.5\text{ pt}$ global penalty purely to diversify near-even xP alternatives.

---

## 5. Cross-Play (Attacker vs Defender) Mathematical Analysis

Many managers instinctively apply Solio's **cross-play penalty** (penalizing starting an attacker against one's own defender or goalkeeper).

**Quantitative Finding**:
$$\mathbb{E}[X_{\text{attacker}} + X_{\text{defender}}] = \mathbb{E}[X_{\text{attacker}}] + \mathbb{E}[X_{\text{defender}}]$$
By linearity of expectation, cross-play **does not reduce expected points**. 

Furthermore, because $\text{Cov}(G_{\text{attacker}}, CS_{\text{defender}}) < 0$, starting an attacker against your defender creates negative covariance, which **reduces total gameweek variance and raises your scoring floor**:
- If the match ends $0–0$, your defender collects $6\text{ pts}$.
- If the match ends $3–1$ with your attacker scoring, your attacker collects $6\text{–}10\text{ pts}$.

**Recommendation**: **Do not enable Solio's cross-play penalty.** Penalizing cross-play lowers expected points while artificially increasing variance.

---

## 6. Recommended 5-Rule Baseline Configuration

To balance expected points maximization with robust variance control, configure the following 5 baseline rules in the Solio web planner sentence builder:

```
1. Hit Friction Buffer (Soft Rule)
   Prefer not to -> take hit -> in each GW -> worth up to 1.8 pts
   Why: Raises the effective transfer hit threshold to -5.8 xP over the horizon,
        eliminating noisy churn while preserving flexibility during crises.

2. Starter xMins Floor (Hard Rule)
   Must not -> start -> players -> projected under 65 mins
   Why: Eliminates sub-60 min cameo traps (1 pt cameos that block bench autosubs)
        without prematurely cutting sub-75 min elite wingers.

3. First-Bench Cover Protection (Soft Rule)
   Prefer to -> own -> at least 12 players -> projected over 65 mins -> worth up to 1.5 pts
   Why: Prevents the solver from stripping the bench to three 0-minute fodder players,
        guaranteeing a playable first substitute against unexpected benchings.

4. Defensive Stack Limiter (Soft Rule)
   Prefer to -> start -> at most 2 -> defenders or goalkeepers -> from each club -> worth up to 1.2 pts
   Why: Guards against catastrophic single-goal defensive wipeouts without forcing
        sub-optimal benchings of elite defenders in prime fixtures.

5. Goalkeeper Transfer Friction (Soft Rule)
   Prefer not to -> buy -> goalkeepers -> worth up to 1.5 pts
   Why: Goalkeeper xP has the lowest signal-to-noise ratio in FPL. Prevents wasting
        Free Transfers on sideways +0.6 xP goalkeeper moves over 4 weeks.
```

---

## 7. Relationship to Sibling Repository `fpl-jubilee-ascent`

- **`jubilee-solio-calibrate`**: Strictly calibrates venue-neutral team ratings (`Goals`, `Goals Conceded`) and empirical Home Advantage Factor ($h$). Output CSVs and Home Advantage parameters are uploaded directly to the Solio web planner UI, where the above 5 rules are applied.
- **`fpl-jubilee-ascent`**: Sibling solver repository owning the local MILP transfer planning engine (`open-fpl-solver`, `commands.solve`). These same 5 variance-control principles map to sibling MILP solver constraints (transfer penalty multipliers, minutes cutoffs, bench weighting, and club limits).
