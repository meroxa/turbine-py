# How to contribute to Turbine-py


## Reporting issues

---
To report a bug, issue, or suggestion please create an issue on this repo's issue tracker.

Include the following in your issue:

- Describe what you expected to happen.
- If possible, include a minimal reproducible example to help us identify the issue.
- Describe what actually happened. Include the full traceback if there was an exception.
- List your Python and Turbine-py versions.


## Submitting code changes

---
First check if there is not a currently existing open issue for the change you want to. Please open a new issue if one does not already exist.

### First time setup

- Download and install the [latest version of git](https://git-scm.com/downloads)
- Make sure you have a [GitHub Account](https://github.com/join)
- [Clone](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#step-2-create-a-local-clone-of-your-fork) Turbine-py locally

    ```bash
    $ git clone https://github.com/meroxa/turbine-py
    $ cd turbine-py
    ```
- Create a virtual environment
  - Linux/macOS
    ```bash
    $ python3 -m venv env
    $ . env/bin/activate
    ```
  - Windows
    ```bash
    > py -3 -m venv env
    > env\Scripts\activate
    ```

- Upgrade pip and setuptools.
    ```bash
    $ python -m pip install --upgrade pip setuptools
    ```

- Install the development dependencies and install turbine-py in editable mode
  ```bash
  make install-dev
  ```

- Install the pre-commit hooks
  ```bash
  make install-hooks
  ```

### Building only the function runtime
You are able to only want to install the dependencies for the function runtime of turbine-py if your changes are limted only to that.

```bash
make funtime
```

### Linting the code
Pre-commit hooks will automatically run linting on your code before you can create a commit. You can run linting before creating a commit if you would prefer.

```bash
make lint
```

### Running tests

Run the basic test suite with pytest.

```bash
$ pytest
```

This runs the tests for the current environment, which is usually sufficient. CI will run the full suite when you submit your pull request.
You can run the full test suite with tox if you don't want to wait.

```bash
$ make test
```
