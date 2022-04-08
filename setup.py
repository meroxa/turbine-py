#!/usr/bin/env python
from logging.config import fileConfig
from setuptools import setup, find_namespace_packages

setup(
    name="turbine-py",
    version="0.0.1",
    description="",
    package_dir={"": "src"},
    include_package_data=True,
    packages=[
        "turbine",
        "turbine.runtime",
        "turbine.runner",
        "turbine.function-deploy",
    ],
    package_data={'turbine': ['config.env']},
    entry_points={
        "console_scripts": ["turbine-py=turbine.cli:main"],
    },
    install_requires=["aiohttp"],
)
