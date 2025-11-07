# MCEvidence

A Python package implementing the **Marginal Likelihoods from Monte Carlo Markov Chains** algorithm described in [Heavens et al. (2017)](http://adsabs.harvard.edu/abs/2017arXiv170403472H).

## Features

- ✅ Bayesian evidence estimation using k-nearest neighbors
- ✅ Support for **CosmoMC** and **Cobaya** MCMC chain formats
- ✅ Automatic format detection
- ✅ Parameter selection (cosmological only or with nuisance parameters)
- ✅ Python 3.8+ support

This code has been modernized and tested with Python 3.8+.

## Installation

### Requirements

- Python 3.8 or higher
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- scikit-learn
- pandas
- PyYAML (optional, required for Cobaya format support)

### Install from source

```bash
git clone https://github.com/yabebalFantaye/MCEvidence
cd MCEvidence
pip install -e .
```

### Install directly from GitHub

```bash
pip install git+https://github.com/yabebalFantaye/MCEvidence
```

## Quick Start

### Basic Usage (Python)

```python
from MCEvidence import MCEvidence

# Calculate Bayesian evidence
mce = MCEvidence('/path/to/chain', kmax=5, burnlen=0.3)
ln_evidence = mce.evidence()
print(f"ln(Z) = {ln_evidence[1]:.3f}")  # k=2 is most stable
```

### Cobaya Format Support

MCEvidence now **automatically detects and supports Cobaya MCMC chains**:

```python
from MCEvidence import MCEvidence

# Works with both CosmoMC and Cobaya formats
mce = MCEvidence('/path/to/cobaya_chain', kmax=5, burnlen=0.3)

# Use only cosmological parameters (recommended for model comparison)
if hasattr(mce.gd, 'cobaya_param_info'):
    param_info = mce.gd.cobaya_param_info
    mce.ndim = param_info['n_cosmo']  # Use only cosmological params

ln_evidence = mce.evidence()
```

**Key differences between CosmoMC and Cobaya formats:**

| Feature     | CosmoMC           | Cobaya                           |
| ----------- | ----------------- | -------------------------------- |
| File naming | `basename_N.txt`  | `basename.N.txt`                 |
| Header      | No header         | `# comment lines`                |
| Config file | `.ranges`         | `.updated.yaml` or `.input.yaml` |
| Parameters  | All in chain file | Sampled + derived parameters     |

For more details, see [COBAYA_USAGE_GUIDE.md](./COBAYA_USAGE_GUIDE.md).

### Command Line Usage

```bash
# Basic usage
python MCEvidence.py /path/to/chain

# With options
python MCEvidence.py /path/to/chain -k 5 -b 0.3 -t 1 -v 1

# See all options
python MCEvidence.py -h
```

## Command Line Options

```
usage: MCEvidence.py [-h] [-k KMAX] [-ic IDCHAIN] [-np NDIM] [-b BURNFRAC]
                     [-t THINFRAC] [-v VERBOSE] [--cosmo] [--allparams]
                     [--paramsfile PARAMSFILE] [--cross]
                     root_name

positional arguments:
  root_name             Root filename for MCMC chains

optional arguments:
  -h, --help            Show help message
  -k KMAX, --kmax KMAX  Maximum k for k-NN (default: 5, use k=2 for final results)
  -ic IDCHAIN, --idchain IDCHAIN
                        Which chains to use (e.g., 1 means read only *_1.txt)
  -np NDIM, --ndim NDIM Number of parameters to use
  -b BURNFRAC, --burnfrac BURNFRAC
                        Burn-in fraction (default: 0.3)
  -t THINFRAC, --thin THINFRAC
                        Thinning fraction (default: 1, no thinning)
  -v VERBOSE, --verbose VERBOSE
                        Verbosity level (0: WARNING, 1: INFO, 2: DEBUG)
  --cosmo               Use only cosmological parameters
  --allparams           Use all parameters (including derived)
  --paramsfile          File with additional parameter names
  --cross               Compute cross-evidence using split chains
```

## Examples

### Model Comparison

```python
from MCEvidence import MCEvidence

# Calculate evidence for Model A
mce_a = MCEvidence('/chains/model_a', kmax=5, burnlen=0.3)
if hasattr(mce_a.gd, 'cobaya_param_info'):
    mce_a.ndim = mce_a.gd.cobaya_param_info['n_cosmo']
ln_Z_a = mce_a.evidence()[1]  # Use k=2

# Calculate evidence for Model B
mce_b = MCEvidence('/chains/model_b', kmax=5, burnlen=0.3)
if hasattr(mce_b.gd, 'cobaya_param_info'):
    mce_b.ndim = mce_b.gd.cobaya_param_info['n_cosmo']
ln_Z_b = mce_b.evidence()[1]  # Use k=2

# Bayes factor
delta_ln_Z = ln_Z_b - ln_Z_a
print(f"Δln(Z) = {delta_ln_Z:.3f}")
print(f"Bayes factor = {np.exp(delta_ln_Z):.2e}")

# Interpretation
if abs(delta_ln_Z) < 1:
    print("No strong preference")
elif delta_ln_Z > 2.5:
    print("Strong evidence for Model B")
elif delta_ln_Z < -2.5:
    print("Strong evidence for Model A")
```

### Jupyter Notebook Example

See [notebook/get_lnZ.ipynb](./notebook/get_lnZ.ipynb) for a complete interactive example with visualization.

### Advanced Example

See [planck_mcevidence.py](./planck_mcevidence.py) for an advanced example analyzing Planck MCMC chains, used in the companion paper [No evidence for extensions to the standard cosmological model](http://adsabs.harvard.edu/abs/2017arXiv170403467H).

## Documentation

- [COBAYA_USAGE_GUIDE.md](./COBAYA_USAGE_GUIDE.md) - Detailed guide for using MCEvidence with Cobaya chains
- [COBAYA_IMPLEMENTATION_SUMMARY.md](./COBAYA_IMPLEMENTATION_SUMMARY.md) - Technical implementation details

## Citation

If you use this code, please cite:

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### Version 2.0 (2025)

- ✅ Added support for Cobaya MCMC chain format
- ✅ Automatic format detection (CosmoMC vs Cobaya)
- ✅ Parameter classification (cosmological vs nuisance vs derived)
- ✅ Modernized for Python 3.8+
- ✅ Improved dependencies (scikit-learn, updated NumPy/SciPy)
- ✅ Bug fixes (thin() method, DistanceMetric import, format detection)

### Version 1.0

- Initial release with CosmoMC support
