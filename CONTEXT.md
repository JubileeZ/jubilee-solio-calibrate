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
