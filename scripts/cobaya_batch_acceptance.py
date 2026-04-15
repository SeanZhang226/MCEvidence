#!/usr/bin/env python3
"""Generate Cobaya test chains in batch and verify MCEvidence can read them."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import numpy as np

from cobaya.run import run

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from MCEvidence import MCEvidence


def build_info(output_prefix: Path, max_samples: int, seed: int, mean_shift: float) -> dict:
    return {
        "likelihood": {
            "gaussian_mixture": {
                "means": [[mean_shift, -mean_shift]],
                "covs": [[[1.0, 0.2], [0.2, 1.2]]],
            }
        },
        "params": {
            "x": {"prior": {"min": -5, "max": 5}, "ref": 0.0, "proposal": 0.35},
            "y": {"prior": {"min": -5, "max": 5}, "ref": 0.0, "proposal": 0.35},
        },
        "sampler": {
            "mcmc": {
                "max_samples": max_samples,
                "burn_in": 0,
                "learn_proposal": False,
                "Rminus1_stop": 1.0,
                "Rminus1_cl_stop": 1.0,
            }
        },
        "output": str(output_prefix),
        "force": True,
        "debug": False,
        "seed": int(seed),
    }


def run_single_dataset(output_prefix: Path, max_samples: int, burnfrac: float, seed: int, mean_shift: float) -> dict:
    info = build_info(output_prefix=output_prefix, max_samples=max_samples, seed=seed, mean_shift=mean_shift)
    run(info, no_mpi=True)

    mce = MCEvidence(str(output_prefix), kmax=3, burnlen=burnfrac, verbose=1)
    lnz = mce.evidence(verbose=0)

    if not np.all(np.isfinite(lnz)):
        raise RuntimeError(f"Non-finite ln(Z) for {output_prefix}: {lnz}")

    param_info = getattr(mce.gd, "cobaya_param_info", None)
    if not param_info or param_info.get("n_sampled") != 2:
        raise RuntimeError(f"Cobaya parameter metadata missing/invalid for {output_prefix}: {param_info}")

    return {
        "prefix": str(output_prefix),
        "samples_after_burn": int(mce.nsample[0] if isinstance(mce.nsample, (list, tuple)) else mce.nsample),
        "lnZ_k1": float(lnz[0]),
        "lnZ_k2": float(lnz[1]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Cobaya batch-data acceptance test for MCEvidence")
    parser.add_argument("--outdir", default="tmp_cobaya_batch", help="Directory for generated Cobaya chains")
    parser.add_argument("--datasets", type=int, default=3, help="Number of test datasets to generate")
    parser.add_argument("--max-samples", type=int, default=160, help="Accepted MCMC samples per dataset")
    parser.add_argument("--burnfrac", type=float, default=0.1, help="Burn-in fraction used by MCEvidence")
    parser.add_argument("--keep", action="store_true", help="Keep generated chains after run")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    results = []
    for idx in range(1, args.datasets + 1):
        prefix = outdir / f"dataset_{idx}"
        result = run_single_dataset(
            output_prefix=prefix,
            max_samples=args.max_samples,
            burnfrac=args.burnfrac,
            seed=202600 + idx,
            mean_shift=0.15 * idx,
        )
        results.append(result)

    print("\nAcceptance summary (Cobaya -> MCEvidence)")
    for row in results:
        print(
            f"- {row['prefix']}: nsample={row['samples_after_burn']}, "
            f"lnZ(k=1)={row['lnZ_k1']:.6f}, lnZ(k=2)={row['lnZ_k2']:.6f}"
        )

    if not args.keep:
        shutil.rmtree(outdir)


if __name__ == "__main__":
    main()
