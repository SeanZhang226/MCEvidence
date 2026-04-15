#!/usr/bin/env python

import io
import re
import os
from setuptools import find_packages, setup


def find_version():
    version_file = io.open(
        os.path.join(os.path.dirname(__file__), "MCEvidence.py")
    ).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="MCEvidence",
    version=find_version(),
    description="MCEvidence evidence estimation from MCMC chains",
    author="Yabebal Fantaye",
    author_email="yabi@aims.ac.za",
    url="https://github.com/yabebalFantaye/MCEvidence",
    packages=find_packages(include=["mcevidence", "mcevidence.*"]),
    py_modules=["MCEvidence"],
    entry_points={"console_scripts": ["mcevidence=mcevidence.core:main"]},
    python_requires=">=3.8",
    # package_data={'planck_fullgrid_R2': ['AllChains','SingleChains']}
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "getdist": ["getdist>=1.3.0"],
        "cobaya": ["cobaya>=3.0.0", "PyYAML>=6.0"],
        "dev": ["pytest>=8.0", "pytest-cov>=5.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=[
        "MCMC",
        "Evidence",
        "bayesian evidence",
        "marginal likelihood",
        "cosmology",
    ],
)
