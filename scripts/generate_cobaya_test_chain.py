"""Generate a realistic tiny Cobaya MCMC chain for integration tests.

The chain uses Cobaya's built-in Gaussian-mixture likelihood and writes
multiple chain files with several sampled parameters plus one nuisance-like
parameter to better mimic real cosmology workflows.
"""

from __future__ import annotations

from cobaya.run import run


def main() -> None:
    info = {
        "likelihood": {
            "gaussian_mixture": {
                "means": [[0.0, 0.0, 0.0, 0.0]],
                "covs": [
                    [
                        [1.0, 0.2, 0.1, 0.0],
                        [0.2, 1.2, 0.05, -0.1],
                        [0.1, 0.05, 0.8, 0.15],
                        [0.0, -0.1, 0.15, 1.1],
                    ]
                ],
            }
        },
        "params": {
            "omega_b": {"prior": {"min": -4, "max": 4}, "proposal": 0.35},
            "omega_cdm": {"prior": {"min": -4, "max": 4}, "proposal": 0.35},
            "n_s": {"prior": {"min": -4, "max": 4}, "proposal": 0.35},
            "A_planck": {"prior": {"min": -4, "max": 4}, "proposal": 0.35},
        },
        "sampler": {"mcmc": {"max_samples": 120, "burn_in": 0}},
        "output": "tests/data/cobaya_from_cobaya",
    }
    run(info, force=True)


if __name__ == "__main__":
    main()
