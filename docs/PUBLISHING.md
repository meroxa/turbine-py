# Publishing a new version of Turbine-py

---

## Automatic Publishing

New versions of Turbine-py are handled by [Python Semantic Release](https://python-semantic-release.readthedocs.io/en/latest/index.html#python-semantic-release).

Python Semantic Release will detect what the next version of the project should be based on the commits. Commits will need to follow [Angular Commit Guidelines](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines)

## Manual Publishing
In order to publish a new version manually, follow the below steps.

Publishing a new version requires the following actions be taken in order:
1. Open a new Pull Request updating version in the [package init file](/src/turbine/__init__.py)
   1. Make sure the commit message is only a version (e.g.: `v1.2.3`)
2. Create a tag on main after merging the above pull request into main
   ```bash
   $ git tag v1.1.0
   $ git push origin tag v1.1.0
   ```

3. Once the tag has been pushed, [create a new release](https://github.com/meroxa/turbine-py/releases/new) with a newly pushed tag
   - `Generate Release Notes` will create an annotated diff of changes since last release for the notes
4. Once the release is published, GitHub Actions will package and publish a new version of turbine-py to [PyPI](https://pypi.org/project/turbine-py/)
