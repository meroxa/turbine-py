
#!/usr/bin/env python
from ensurepip import version
from setuptools import setup, find_packages

setup(name="Turbine-py",
version="1.0",
description="",
package_dir={'': 'src'},
packages=['turbine', 'turbine.runtime']
      )
