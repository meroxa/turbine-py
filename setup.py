
#!/usr/bin/env python
from glob import glob
from importlib.metadata import entry_points
from setuptools import setup

setup(
    name="turbine",
    version="0.0.1",
    description="",
    package_dir={'': 'src'},
    include_package_data=True,
    packages=['turbine', 'turbine.runtime', 'turbine.templates'],
    entry_points={
        'console_scripts': ['turbine=turbine.cli:main'],
    }
)
