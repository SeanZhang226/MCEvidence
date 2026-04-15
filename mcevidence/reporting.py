"""Report generation helpers for MCEvidence runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

import numpy as np


def build_report_dict(
    *,
    method: str,
    chain_format: str,
    selected_param_names: Iterable[str],
    nparams_mc: int,
    ndim_used: int,
    nsamples_read: Any,
    nsamples_used: Any,
    prior_volume: float,
    lnz_values: Iterable[float],
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Create a structured report dictionary for a run."""
    lnz = np.asarray(list(lnz_values), dtype=float).tolist()
    payload: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "chain_format": chain_format,
        "selected_param_names": list(selected_param_names),
        "nparams_mc": int(nparams_mc),
        "ndim_used": int(ndim_used),
        "nsamples_read": nsamples_read,
        "nsamples_used": nsamples_used,
        "prior_volume": float(prior_volume),
        "lnz_values": lnz,
    }
    if extra:
        payload["extra"] = extra
    return payload


def write_report(path: str, payload: Dict[str, Any], report_format: str = "json") -> str:
    """Write report payload to disk in json or txt format."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    fmt = report_format.lower()
    if fmt == "json":
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif fmt == "txt":
        lines = []
        for key, val in payload.items():
            lines.append(f"{key}: {val}")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        raise ValueError("Unsupported report format. Use 'json' or 'txt'.")

    return str(out)
