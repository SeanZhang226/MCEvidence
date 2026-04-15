"""Helpers for selecting active parameter subspaces for lnZ estimation."""

from __future__ import annotations

from typing import Callable, Iterable, List, Sequence, Tuple

import numpy as np


def resolve_parameter_selection(
    available_param_names: Sequence[str],
    nparam_mc: int,
    param_names: Iterable[str] | None,
    use_cosmo_params: bool,
    ndim: int | None,
    is_cosmo_name: Callable[[str], bool],
    cobaya_cosmo_names: Sequence[str] | None = None,
) -> Tuple[np.ndarray, List[str], bool]:
    """Resolve selected parameter indices and names.

    Returns
    -------
    param_indices
        Integer indices into the sample parameter columns.
    selected_names
        Ordered names for selected parameters.
    fallback_all
        True when `use_cosmo_params=True` but no cosmo names are found and
        the function falls back to all sampled parameters.
    """
    names = list(available_param_names[:nparam_mc])

    selected_names: List[str] | None = None
    fallback_all = False

    if param_names:
        selected_names = [p.strip() for p in param_names if p and p.strip()]
    elif use_cosmo_params:
        if cobaya_cosmo_names:
            selected_names = [p for p in cobaya_cosmo_names if p in names]
        else:
            selected_names = [p for p in names if is_cosmo_name(p)]

        if not selected_names:
            fallback_all = True
            selected_names = None

    if selected_names:
        missing = [p for p in selected_names if p not in names]
        if missing:
            raise ValueError("Requested parameters not found in chain: " + ", ".join(missing))
        indices = np.array([names.index(p) for p in selected_names], dtype=int)
    else:
        indices = np.arange(nparam_mc, dtype=int)
        selected_names = names.copy()

    if ndim is not None:
        indices = indices[:ndim]
        selected_names = selected_names[:ndim]

    if len(indices) < 1:
        raise ValueError("At least one parameter must be selected for lnZ estimation.")

    return indices, selected_names, fallback_all
