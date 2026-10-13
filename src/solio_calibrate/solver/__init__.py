"""Solio squad optimization solver package integrating vendored open-fpl-solver."""

from solio_calibrate.solver.adapter import (
    calculate_effective_horizon,
    format_confirmation_summary,
    format_solution_table,
    generate_fplteam_link,
    solve_squad,
)

__all__ = [
    "calculate_effective_horizon",
    "format_confirmation_summary",
    "format_solution_table",
    "generate_fplteam_link",
    "solve_squad",
]
