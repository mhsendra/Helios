"""Financial calculations used by Helios."""

import numpy as np


class NoRealSolutionError(ValueError):
    """Raised when no real IRR solution exists."""


def _irr_default_selection(eirr):
    """Select an IRR using numpy-financial 1.1.0 default logic."""
    same_sign = np.all(eirr > 0) if eirr[0] > 0 else np.all(eirr < 0)

    if not same_sign:
        positive = np.sum(eirr[eirr > 0])
        negative = np.sum(eirr[eirr < 0])

        if positive >= negative:
            eirr = eirr[eirr >= 0]
        else:
            eirr = eirr[eirr < 0]

    return eirr[np.argmin(np.abs(eirr))]


def irr(values, *, raise_exceptions=False, selection_logic=_irr_default_selection):
    """Calculate the internal rate of return without native extensions."""
    values = np.atleast_2d(values)

    if values.ndim != 2:
        raise ValueError("Cashflows must be a 2D array")

    results = np.empty(values.shape[0], dtype=float)

    for index, row in enumerate(values):
        same_sign = (
            np.all(row > 0)
            if row[0] > 0
            else np.all(row < 0)
        )

        if same_sign:
            if raise_exceptions:
                raise NoRealSolutionError(
                    "No real solution exists for IRR since all cashflows "
                    "are of the same sign."
                )
            results[index] = np.nan
            continue

        roots = np.roots(row)
        solutions = np.real(roots[np.isreal(roots)]) - 1
        solutions = solutions[solutions >= -1]

        if len(solutions) == 0:
            if raise_exceptions:
                raise NoRealSolutionError(
                    "No real solution is found for IRR."
                )
            results[index] = np.nan
        elif len(solutions) == 1:
            results[index] = solutions[0]
        else:
            results[index] = selection_logic(solutions)

    try:
        return results.item()
    except ValueError:
        return results.squeeze()
