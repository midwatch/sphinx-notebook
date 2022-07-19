from pathlib import Path

from invoke import Collection
from invoke import task
from invoke.exceptions import Failure

from mw_dry_invoke import git

GITHUB_USERNAME = "midwatch"
GITHUB_SLUG = "sphinx-notebook"
SOLUTION_SLUG = "sphinx_notebook"
CC_VERSION = "0.0.0"

ROOT_DIR = Path(__file__).parent
SOURCE_DIR = ROOT_DIR.joinpath("sphinx_notebook")
TEST_DIR = ROOT_DIR.joinpath("tests")

PYTHON_DIRS_STR = " ".join([str(_dir) for _dir in [SOURCE_DIR, TEST_DIR]])


@task
def clean_build(ctx):
    """
    Clean up files from package building
    """
    ctx.run("rm -fr build/")
    ctx.run("rm -fr dist/")
    ctx.run("rm -fr .eggs/")
    ctx.run("find . -name '*.egg-info' -exec rm -fr {} +")
    ctx.run("find . -name '*.egg' -exec rm -f {} +")


@task
def clean_python(ctx):
    """
    Clean up python file artifacts
    """
    ctx.run("find . -name '*.pyc' -exec rm -f {} +")
    ctx.run("find . -name '*.pyo' -exec rm -f {} +")
    ctx.run("find . -name '*~' -exec rm -f {} +")
    ctx.run("find . -name '__pycache__' -exec rm -fr {} +")


@task
def lint_pycodestyle(ctx):
    """Lint code with pycodestyle"""
    ctx.run(f'poetry run pycodestyle --max-line-length=120 {SOURCE_DIR}')


@task
def lint_pydocstyle(ctx):
    """Lint code with pydocstyle"""
    ctx.run(f'poetry run pydocstyle {SOURCE_DIR}')


@task
def lint_pylint(ctx):
    """Lint code with pylint"""
    ctx.run(f'poetry run pylint {PYTHON_DIRS_STR}')


@task(help={'part': "major, minor, or patch/hotfix"})
def bumpversion(ctx, part):
    """Bump project version

    Raises:
        Failure: part not in [major, minor, patch]
    """
    part = 'patch' if part == 'hotfix' else part

    if part not in ['major', 'minor', 'patch']:
        raise Failure('Not a valid part')

    ctx.run(f'poetry run bump2version --no-tag {part}')


@task(pre=[clean_build, clean_python])
def clean(ctx):
    """
    Runs all clean sub-tasks
    """
    pass


@task(clean)
def build(ctx):
    """
    Build source and wheel packages
    """
    ctx.run("poetry build")


@task(help={'check': "Checks if source is formatted without applying changes"})
def format_yapf(ctx, check=False):
    """Format code"""
    yapf_options = '--recursive {}'.format('--diff' if check else '--in-place')
    ctx.run(f'poetry run yapf {yapf_options} {PYTHON_DIRS_STR}')

    isort_options = '{}'.format('--check-only --diff' if check else '')
    ctx.run(f'poetry run isort {isort_options} {PYTHON_DIRS_STR}')


@task
def init_repo(ctx):
    """Initialize freshly cloned repo"""
    ctx.run('poetry install')
    git.init(ctx)


@task(lint_pylint, lint_pycodestyle, lint_pydocstyle)
def lint(ctx):
    """Run all linters"""


@task(pre=[clean, build])
def release(ctx):
    """
    Make a release of the python package to pypi
    """
    ctx.run("poetry publish")


@task(clean)
def test_accept(ctx):
    """Build test notebook"""
    ctx.run('mkdir -p build')
    ctx.run('cp -r tests/fixtures/notebook build/rst')
    ctx.run('poetry run sphinx_notebook new note build/rst/section_1/test_note.rst')
    ctx.run("sed -i 's/New Note/Test Note/' build/rst/section_1/test_note.rst")

    ctx.run(f'poetry run sphinx_notebook build build/rst build/rst/index.rst')
    ctx.run('poetry run sphinx-build -b html build/rst build/www')


@task
def test_pytest(ctx):
    """Run tests"""
    ctx.run('poetry run pytest')


@task(test_pytest, test_accept)
def test(ctx):
    """Run tests"""


ns = Collection(build, bumpversion, clean, init_repo, lint, release, test, test_pytest)
ns.add_task(format_yapf, name="format")

ns.add_collection(git.collection, name="scm")
