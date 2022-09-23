## Publishing a new version 

Publishing a new version requires the following actions be taken in order:
1. Open a new Pull Request updating [VERSION.txt](../VERSION.txt)
2. Create a tag on main after merging the above pull request into main
   ```bash
   $ git tag v1.1.0 
   $ git push origin tag v1.1.0
   ```
3. New tags will trigger the [tagged-release](../.github/workflows/tagged-release.yml) workflow, creating a new release based on your new tag
4. Once the release is published, GitHub Actions will package and publish a new version of turbine-py to [PyPI](https://pypi.org/project/turbine-py/)