# MCEvidence

MCEvidence estimates Bayesian evidence (`ln Z`) from MCMC chains with the k-nearest-neighbour method of Heavens et al. (2017).

## Highlights

- Cobaya-first workflow (default chain format)
- Explicit format control: `cobaya`, `cosmomc`, `auto`
- Flexible parameter selection:
  - all sampled params (default)
  - cosmological subset (`--cosmo`)
  - fully custom list (`--select-params` / `--select-params-file`)
- Python 3.8+ compatible packaging (`pyproject.toml`)
- Multi-chain test fixtures for Cobaya and CosmoMC
- Modular package layout for easier maintenance (`mcevidence/`)

## Install

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e .[cobaya]
pip install -e .[dev]
```

## Quick start

```bash
# Cobaya default format, all sampled params
mcevidence tests/data/cobaya_multi -k 3 -vb 1

# Use only cosmological subset
mcevidence tests/data/cobaya_multi --cosmo -k 3 -vb 1

# Custom parameter subset
mcevidence tests/data/cobaya_multi --select-params p1,p2,p3 -k 3 -vb 1

# CosmoMC explicit format
mcevidence tests/data/cosmomc_multi --format cosmomc --allparams -np 8 -k 3 -vb 1

# Save a full run report
mcevidence tests/data/cobaya_multi --select-params p1,p2 --report-file out/report.json --report-format json -k 3 -vb 1
```

## Parameter classification behavior

### Cobaya

- Sampled params are read from `root.updated.yaml` / `root.input.yaml` / `root.yaml` when available.
- Cosmological params are identified by known cosmology-name rules; unknown new-physics parameters are **not automatically tagged as cosmological**.
- For new model parameters, use `--select-params` (recommended) or add names via `--paramsfile` if you want them included in `--cosmo` mode.

### CosmoMC

- Parameter names come from `root.ranges`.
- `--cosmo` uses an internal known-cosmology name list.
- New parameters are not auto-cosmological by default; use `--select-params` or `--allparams`.

## Testing

```bash
pytest -q
```

The repository includes realistic test fixtures:

- multi-chain Cobaya dataset: `tests/data/cobaya_multi.*`
- multi-chain CosmoMC dataset: `tests/data/cosmomc_multi_*`
- Cobaya-generated chain: `tests/data/cobaya_from_cobaya.*`

Regenerate Cobaya-native fixture:

```bash
python scripts/generate_cobaya_test_chain.py
```

## Output report

Use `--report-file` to save a complete run summary (`json` or `txt`) including:

- selected parameter names
- chain format and sample counts
- prior volume and lnZ values
- optional extra context metadata

## Internal module layout

- `mcevidence/core.py`: main `MCEvidence` class + CLI implementation
- `mcevidence/parameter_selection.py`: parameter-subspace selection logic
- `mcevidence/reporting.py`: run report payload + file writing
- `MCEvidence.py`: backward-compatible thin wrapper

## Citation

```bibtex
@article{Heavens2017,
  author = {Heavens, Alan and Fantaye, Yabebal and Sellentin, Elena and Eggers, Hans and Hosenie, Zafiirah and Kroon, Steve and Mootoovaloo, Arrykrishna},
  title = {No evidence for extensions to the standard cosmological model},
  journal = {Physical Review Letters},
  year = {2017},
  volume = {119},
  pages = {101301},
  doi = {10.1103/PhysRevLett.119.101301}
}
```

## License

MIT
