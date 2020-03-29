#!/usr/bin/env python3

import os
import shutil

from setuptools import setup, find_packages

if not os.path.exists("bin"):
    os.makedirs("bin")

shutil.copy("main.py", "bin/diffuse")

setup(
    name="Diffuse",
    version="0.5.0",
    scripts=["bin/diffuse"],

    packages=find_packages(),
    # package_dir={"": "src"},
    # packages=find_packages("src"),
)

shutil.rmtree("bin")
