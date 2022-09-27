## Publishing a new version

Publishing a new version requires the following actions be taken in order:
1. Open a new Pull Request updating [VERSION.txt](../VERSION.txt)
2. Create a tag on main after merging the above pull request into main
   ```bash
   $ git tag v1.1.0
   $ git push origin tag v1.1.0
   ```

3. Once the tag has been pushed, [create a new release](https://github.com/meroxa/turbine-py/releases/new) with a newly pushed tag
   - `Generate Release Notes` will create an annotated diff of changes since last release for the notes
4. Once the release is published, GitHub Actions will package and publish a new version of turbine-py to [PyPI](https://pypi.org/project/turbine-py/)
