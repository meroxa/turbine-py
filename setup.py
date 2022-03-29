#!/usr/bin/env python
from setuptools import setup, find_namespace_packages

setup(
    name="turbine",
    version="0.0.1",
    description="",
    package_dir={'': 'src'},
    include_package_data=True,
    packages=['turbine', 'turbine.runtime'],
    entry_points={
        'console_scripts': ['turbine=turbine.cli:main'],
    },
    install_requires = [
        "aiohttp"
    ]
)
