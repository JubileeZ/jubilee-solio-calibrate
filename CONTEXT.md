# jubilee-solio-calibrate Glossary

Domain vocabulary for calibrating Solio team attack and defense strengths against Premier League match data.

## Language

**Base Strength**:
The pre-existing attacking (`Goals`) and defensive (`Goals Conceded`) expected rates imported from Solio web planner exports.
_Avoid_: Solio prior, raw strength, uncalibrated rating.

**FPL Empirical Form**:
A team's observed per-match performance derived from official Fantasy Premier League fixture data and underlying metrics (Goals, Goals Conceded, Expected Goals, Expected Goals Conceded) across finished matches in the current season.
_Avoid_: Preference, preference value, raw form, user preference.

**Expected Goals (xG)**:
The statistical quality of scoring chances created by a team in finished matches, sourced from official FPL player event metrics and aggregated to the team level.
_Avoid_: Predicted goals, shot quality.

**Expected Goals Conceded (xGC)**:
The statistical quality of scoring chances conceded by a team to opponents in finished matches, equivalent to the opponent's total xG conceded.
_Avoid_: Defensive xG, conceded chance quality.

**Opponent Difficulty Normalization**:
A mathematical adjustment applied to a team's scoring and conceding rates based on the relative defensive and attacking strengths of the specific opponents faced to date, discounting performances against weak opponents and rewarding performances against strong opponents.
_Avoid_: SOS adjustment, fixture damping, handicap.

**Calibrated Strength**:
The final synthesized team attack (`Goals`) and defense (`Goals Conceded`) ratings obtained by blending Base Strength and normalized FPL Empirical Form, formatted to 3 decimal places for Solio export.
_Avoid_: Adjusted rating, final score, output strength.

**Home Advantage Factor**:
The single league-wide percentage adjustment $h$ applied symmetrically to team expected goals based on venue ($\text{Home} = \text{Goals} \times (1 + h)$, $\text{Away} = \text{Goals} \times (1 - h)$). The empirical value is derived from season-to-date Premier League fixture outcomes. Solio's configured default may change, so do not assume or report a fixed default value.
_Avoid_: Home bias, venue split, home handicap.

**Active Base Strength**:
The currently active uncalibrated Solio export residing at `data/raw/team_strengths_base.csv`, serving as the default prior baseline for calibration.
_Avoid_: Default raw file, current raw input, source file.

**Raw Input Archive**:
Chronologically archived historical base strength CSV exports stored under `data/raw/archive/` using timestamped filenames (`team_strengths_base_YYYY-MM-DD_HH-MM-SS.csv`).
_Avoid_: Raw backup, raw subrepo, old inputs.

**Latest Calibrated Output**:
The most recently computed calibrated ratings written to `data/output/team_strengths_calibrated.csv`, formatted strictly to 3 decimal places and ready for direct upload to the Solio web planner.
_Avoid_: Latest strength, current output file, active export.

**Calibrated Output Archive**:
Chronologically archived historical calibrated CSV exports stored under `data/output/archive/` using timestamped filenames (`team_strengths_calibrated_YYYY-MM-DD_HH-MM-SS.csv`).
_Avoid_: Output backup, output subrepo, run history folder.

**Provisional Match**:
A Premier League match where the final whistle has blown and live statistics (goals, xG) are recorded by the FPL API, but bonus points or official data audits have not yet finalized (`finished_provisional = true`, `finished = false`).
_Avoid_: Live match, in-progress game, tentative fixture.

**Gameweek Coverage**:
The numerical range of Premier League rounds incorporated into a calibration run, identified by the highest completed gameweek plus any provisionally finished matches in the current gameweek.
_Avoid_: Round window, matchweek span, GW count.

**Player Projection**:
Multi-gameweek expected minutes (`_xMins`) and expected points (`_Pts`) per player exported from the Solio web planner after calibrated team strengths are applied.
_Avoid_: Player prediction, raw points, solver input csv.

**Multi-Period Solve**:
An integer linear programming optimization (via HiGHS) maximizing cumulative projected points over a planning horizon subject to FPL squad, budget, transfer, and chip rules.
_Avoid_: Squad optimization run, lineup calculate, team solver.

**Manager Team State**:
The active 15-player squad, bank balance, available chips, and accumulated free transfers for an FPL entry.
_Avoid_: User picks, current team json, manager profile.

**Transfer Plan**:
The optimal gameweek-by-gameweek schedule of transfers, starting eleven, captaincy, and bench order.
_Avoid_: Solution route, move list, solver schedule.


