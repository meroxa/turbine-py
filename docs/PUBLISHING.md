## Publishing a new version 

Publishing a new version requires the following actions be taken in order:
1. Open a new Pull Request updating [VERSION.txt](../VERSION.txt)
2. Create a new release with a new tag that matches the new version once that Pull Request is merged
3. Once the release is made, Github Actions will package and publish a new verison of turbine-py to [PyPI](https://pypi.org/project/turbine-py/)