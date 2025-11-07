#!/usr/bin/env python
"""
测试脚本：使用 Cobaya MCMC 数据计算贝叶斯证据

作者：AI Assistant
日期：2025-10-20

目的：
1. 测试 MCEvidence 对 Cobaya 格式的支持
2. 计算 ΛCDM 和 EDE+PPF 模型的贝叶斯证据
3. 比较不同观测数据组合的模型选择

数据集：
- ΛCDM 模型: CMBBAO, CMBPANBAO, DESY5, Union3
- EDE+PPF 模型: sCMBBAO, sCMBPANBAO, sDESY5, sUnion3
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add MCEvidence to path
sys.path.insert(0, str(Path(__file__).parent))

from MCEvidence import MCEvidence

# Data directory
DATA_DIR = Path("d:/My-project/Cosmology-MCMC/EDE+PPF-model/data-analysis")

# Model configurations
MODELS = {
    "LCDM": {
        "datasets": ["CMBBAO", "CMBPANBAO", "DESY5", "Union3"],
        "description": "ΛCDM (Standard Cosmology)",
    },
    "EDE_PPF": {
        "datasets": ["sCMBBAO", "sCMBPANBAO", "sDESY5", "sUnion3"],
        "description": "Early Dark Energy + PPF",
    },
}

# Evidence calculation parameters
EVIDENCE_PARAMS = {
    "kmax": 5,  # Maximum k for k-NN
    "burnlen": 0.3,  # Burn-in fraction
    "thinlen": 1,  # Thinning (1 = no thinning)
    "verbose": 1,  # Verbosity level
    "split": False,  # Use cross-evidence (slower but more accurate)
}

# Parameter selection mode
# 'cosmo_only' - Use only cosmological parameters (H0, logA, ns, ombh2, omch2, tau, fde_zc, log10_ac, theta_i)
# 'with_nuisance' - Include nuisance parameters (A_planck, amp_143, amp_217, etc.)
# None - Use all sampled parameters (default, determined from Cobaya yaml)
PARAM_MODE = (
    "cosmo_only"  # Change to 'with_nuisance' or None to include more parameters
)


def test_chain_loading(chain_path):
    """
    Test if chain files can be loaded correctly.

    Parameters
    ----------
    chain_path : Path
        Path to chain directory

    Returns
    -------
    dict
        Statistics about the loaded chains
    """
    print(f"\n{'='*70}")
    print(f"Testing chain loading: {chain_path.name}")
    print(f"{'='*70}")

    try:
        # Initialize MCEvidence
        mce = MCEvidence(str(chain_path / chain_path.name), **EVIDENCE_PARAMS)

        # Get chain statistics
        stats = {
            "dataset": chain_path.name,
            "n_chains": len(mce.gd.chains) if hasattr(mce.gd, "chains") else "merged",
            "n_samples_total": mce.gd.get_shape()[0],
            "n_params": mce.gd.get_shape()[1],
            "ndim_used": mce.ndim,
            "status": "SUCCESS",
        }

        print(f"[OK] Loaded successfully!")
        print(f"  - Total samples: {stats['n_samples_total']}")
        print(f"  - Parameters: {stats['n_params']}")
        print(f"  - Dimensions used: {stats['ndim_used']}")

        return stats

    except Exception as e:
        print(f"[FAILED] Failed to load: {e}")
        return {"dataset": chain_path.name, "status": "FAILED", "error": str(e)}


def calculate_evidence(chain_path, model_name, dataset_name):
    """
    Calculate Bayesian evidence for a dataset.

    Parameters
    ----------
    chain_path : Path
        Path to chain directory
    model_name : str
        Model name (LCDM or EDE_PPF)
    dataset_name : str
        Dataset name

    Returns
    -------
    dict
        Evidence calculation results
    """
    print(f"\n{'='*70}")
    print(f"Calculating Evidence: {model_name} - {dataset_name}")
    print(f"{'='*70}")

    try:
        # Initialize MCEvidence
        mce = MCEvidence(str(chain_path / dataset_name), **EVIDENCE_PARAMS)

        # Set ndim based on parameter mode
        if PARAM_MODE == "cosmo_only" and hasattr(mce.gd, "cobaya_param_info"):
            param_info = mce.gd.cobaya_param_info
            if param_info:
                # Use only cosmological parameters
                ndim_to_use = param_info["n_cosmo"]
                print(
                    f"Using {ndim_to_use} cosmological parameters (excluding nuisance)"
                )
                print(f"  Cosmo params: {param_info['cosmo_params']}")
                mce.ndim = ndim_to_use
        elif PARAM_MODE == "with_nuisance" and hasattr(mce.gd, "cobaya_param_info"):
            param_info = mce.gd.cobaya_param_info
            if param_info:
                # Use all sampled parameters (cosmo + nuisance)
                ndim_to_use = param_info["n_sampled"]
                print(f"Using {ndim_to_use} sampled parameters (cosmo + nuisance)")
                print(f"  Cosmo: {param_info['cosmo_params']}")
                print(f"  Nuisance: {param_info['nuisance_params']}")
                mce.ndim = ndim_to_use
        # else: use default ndim from MCEvidence initialization

        # Calculate evidence
        print("\nRunning evidence calculation...")
        ln_evidence = mce.evidence()

        # Get results for different k values
        results = {
            "model": model_name,
            "dataset": dataset_name,
            "n_samples": mce.gd.get_shape()[0],
            "ndim": mce.ndim,
            "status": "SUCCESS",
        }

        # Store evidence for each k
        for k_idx, ln_Z in enumerate(ln_evidence, start=1):
            results[f"ln_Z_k{k_idx}"] = ln_Z

        # Use k=2 as default (often most stable)
        results["ln_Z_best"] = (
            ln_evidence[1] if len(ln_evidence) > 1 else ln_evidence[0]
        )

        print(f"\n{'─'*70}")
        print(f"Results:")
        print(f"{'─'*70}")
        for k_idx, ln_Z in enumerate(ln_evidence, start=1):
            print(f"  ln(Z) [k={k_idx}] = {ln_Z:.3f}")
        print(f"{'─'*70}")
        print(f"[OK] Evidence calculation completed!")

        return results

    except Exception as e:
        print(f"[FAILED] Evidence calculation failed: {e}")
        import traceback

        traceback.print_exc()
        return {
            "model": model_name,
            "dataset": dataset_name,
            "status": "FAILED",
            "error": str(e),
        }


def compare_models(results_df):
    """
    Compare models using Bayes factors.

    Parameters
    ----------
    results_df : DataFrame
        Results from evidence calculations
    """
    print(f"\n{'='*70}")
    print("MODEL COMPARISON - BAYES FACTORS")
    print(f"{'='*70}\n")

    # Group by dataset
    datasets = results_df["dataset"].unique()

    comparison_results = []

    for dataset in datasets:
        dataset_results = results_df[results_df["dataset"] == dataset]

        # Get evidence for each model
        lcdm_result = dataset_results[dataset_results["model"] == "LCDM"]
        ede_result = dataset_results[dataset_results["model"] == "EDE_PPF"]

        if len(lcdm_result) == 0 or len(ede_result) == 0:
            continue

        ln_Z_lcdm = lcdm_result["ln_Z_best"].values[0]
        ln_Z_ede = ede_result["ln_Z_best"].values[0]

        # Calculate Bayes factor: B_EDE/LCDM = Z_EDE / Z_LCDM
        ln_BF = ln_Z_ede - ln_Z_lcdm
        BF = np.exp(ln_BF)

        # Interpretation
        if ln_BF > 5:
            interpretation = "Very strong evidence for EDE+PPF"
        elif ln_BF > 2.5:
            interpretation = "Strong evidence for EDE+PPF"
        elif ln_BF > 1:
            interpretation = "Moderate evidence for EDE+PPF"
        elif ln_BF > -1:
            interpretation = "Inconclusive"
        elif ln_BF > -2.5:
            interpretation = "Moderate evidence for ΛCDM"
        elif ln_BF > -5:
            interpretation = "Strong evidence for ΛCDM"
        else:
            interpretation = "Very strong evidence for ΛCDM"

        comparison_results.append(
            {
                "Dataset": dataset,
                "ln(Z_LCDM)": ln_Z_lcdm,
                "ln(Z_EDE)": ln_Z_ede,
                "ln(BF)": ln_BF,
                "BF": BF,
                "Interpretation": interpretation,
            }
        )

        print(f"Dataset: {dataset}")
        print(f"{'─'*70}")
        print(f"  ln(Z_ΛCDM)        = {ln_Z_lcdm:10.3f}")
        print(f"  ln(Z_EDE+PPF)     = {ln_Z_ede:10.3f}")
        print(f"  ln(BF_EDE/LCDM)   = {ln_BF:10.3f}")
        print(f"  BF_EDE/LCDM       = {BF:10.2e}")
        print(f"  Interpretation: {interpretation}")
        print()

    return pd.DataFrame(comparison_results)


def main():
    """
    Main test routine.
    """
    print("\n" + "=" * 70)
    print("MCEvidence - Cobaya Format Support Test")
    print("=" * 70)
    print(f"\nData directory: {DATA_DIR}")
    print(f"Evidence parameters: {EVIDENCE_PARAMS}")

    # Test 1: Check if all chain directories exist
    print(f"\n{'='*70}")
    print("STEP 1: Checking Data Availability")
    print(f"{'='*70}")

    all_datasets = []
    for model_name, model_info in MODELS.items():
        for dataset in model_info["datasets"]:
            dataset_path = DATA_DIR / dataset
            exists = dataset_path.exists()
            status = "[OK]" if exists else "[MISSING]"
            print(f"{status} {model_name:10s} - {dataset:15s} : {dataset_path}")
            if exists:
                all_datasets.append((model_name, dataset, dataset_path))

    if not all_datasets:
        print("\n[FAILED] No datasets found! Please check DATA_DIR path.")
        return

    # Test 2: Try loading chains
    print(f"\n{'='*70}")
    print("STEP 2: Testing Chain Loading")
    print(f"{'='*70}")

    load_results = []
    for model_name, dataset, dataset_path in all_datasets[:2]:  # Test first 2 for speed
        stats = test_chain_loading(dataset_path)
        stats["model"] = model_name
        load_results.append(stats)

    load_df = pd.DataFrame(load_results)
    print("\n" + "=" * 70)
    print("Loading Test Summary:")
    print("=" * 70)
    print(load_df.to_string(index=False))

    # Test 3: Calculate evidence
    print(f"\n{'='*70}")
    print("STEP 3: Calculating Bayesian Evidence")
    print(f"{'='*70}")
    print("\nNote: This may take several minutes per dataset...")

    evidence_results = []
    for model_name, dataset, dataset_path in all_datasets:
        result = calculate_evidence(dataset_path, model_name, dataset)
        evidence_results.append(result)

    evidence_df = pd.DataFrame(evidence_results)

    # Save results
    output_file = Path("evidence_results.csv")
    evidence_df.to_csv(output_file, index=False)
    print(f"\n[OK] Results saved to: {output_file}")

    # Test 4: Model comparison
    successful_results = evidence_df[evidence_df["status"] == "SUCCESS"]
    if len(successful_results) >= 2:
        comparison_df = compare_models(successful_results)
        comparison_file = Path("model_comparison.csv")
        comparison_df.to_csv(comparison_file, index=False)
        print(f"[OK] Comparison results saved to: {comparison_file}")

    # Final summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total datasets tested: {len(all_datasets)}")
    print(f"Successful: {len(successful_results)}")
    print(f"Failed: {len(evidence_df) - len(successful_results)}")

    if len(successful_results) > 0:
        print(f"\nEvidence Results:")
        print("─" * 70)
        for _, row in successful_results.iterrows():
            print(
                f"{row['model']:10s} - {row['dataset']:15s} : ln(Z) = {row['ln_Z_best']:.3f}"
            )

    print(f"\n{'='*70}")
    print("TEST COMPLETED")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
