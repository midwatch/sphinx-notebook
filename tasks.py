from pathlib import Path

from invoke import Collection
from invoke import task
from invoke.exceptions import Failure

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


@task
def scm_init(ctx):
    """Init scm repo (if required).

    Raises:
        Failure: .gitignore does not exist

    Returns:
        None
    """
    if not Path('.gitignore').is_file():
        raise Failure('.gitignore does not exist')

    if not Path('.git').is_dir():
        uri_remote = 'git@github.com:{}/{}.git'.format(GITHUB_USERNAME,
                                                       GITHUB_SLUG
                                                      )

        ctx.run('git init')
        ctx.run('git add .')
        ctx.run('git commit -m "new package from midwatch/cc-py3-pkg ({})"'.format(CC_VERSION))
        ctx.run('git branch -M main')
        ctx.run('git remote add origin {}'.format(uri_remote))
        ctx.run('git tag -a "v_0.0.0" -m "cookiecutter ref"')


@task
def scm_push(ctx):
    """Push all branches and tags to origin."""

    for branch in ('develop', 'main'):
        ctx.run('git push origin {}'.format(branch))

    ctx.run('git push --tags')


@task
def scm_status(ctx):
    """Show status of remote branches."""
    ctx.run('git for-each-ref --format="%(refname:short) %(upstream:track)" refs/heads')


@task(help={'part': "major, minor, or patch"})
def bumpversion(ctx, part):
    """Bump project version

    Raises:
        Failure: part not in [major, minor, patch]
    """
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
def format(ctx, check=False):
    """Format code"""
    yapf_options = '--recursive {}'.format('--diff' if check else '--in-place')
    ctx.run(f'poetry run yapf {yapf_options} {PYTHON_DIRS_STR}')

    isort_options = '{}'.format('--check-only --diff' if check else '')
    ctx.run(f'poetry run isort {isort_options} {PYTHON_DIRS_STR}')


@task
def init(ctx):
    """Initialize freshly cloned repo"""
    ctx.run('poetry install')

    scm_init(ctx)

    ctx.run('git flow init -d')
    ctx.run('git flow config set versiontagprefix v_')

    scm_push(ctx)


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
    """Build notebook"""
    ctx.run('mkdir -p build/simple')
    ctx.run('cp -r tests/fixtures/notes/simple build/simple/rst')
    ctx.run('poetry run sphinx_notebook new note build/simple/rst/section_4/test_note.rst')
    ctx.run("sed -i 's/New Note/Test Note/' build/simple/rst/section_4/test_note.rst")

    ctx.run(f'poetry run sphinx_notebook build  build/simple/rst build/simple/rst/index.rst')
    ctx.run('poetry run sphinx-build -b html build/simple/rst build/simple/www')

    """Build pruned notebook"""
    ctx.run('mkdir -p build/pruned')
    ctx.run('cp -r tests/fixtures/notes/simple build/pruned/rst')

    ctx.run('poetry run sphinx_notebook new note build/pruned/rst/section_1/_include/inc_note_1.rst')
    ctx.run("sed -i 's/New Note/Test Prun Note 1/' build/pruned/rst/section_1/_include/inc_note_1.rst")

    ctx.run('poetry run sphinx_notebook new note build/pruned/rst/section_2/sub_section_2.1/_include/inc_note_2.rst')
    ctx.run("sed -i 's/New Note/Test Prun Note 2/' build/pruned/rst/section_2/sub_section_2.1/_include/inc_note_2.rst")

    # ctx.run(f'poetry run sphinx_notebook build --prune _include build/pruned/rst build/pruned/rst/index.rst')
    ctx.run(f'poetry run sphinx_notebook build build/pruned/rst build/pruned/rst/index.rst')
    ctx.run('poetry run sphinx-build -b html build/pruned/rst build/pruned/www')


    """Build table formatted notebook"""
    ctx.run('mkdir -p build/table')
    ctx.run('cp -r tests/fixtures/notes/table build/table/rst')

    ctx.run(f'poetry run sphinx_notebook build  --template-name index_table.rst.jinja build/table/rst build/table/rst/index.rst')
    ctx.run('poetry run sphinx-build -b html build/table/rst build/table/www')


@task
def test_pytest(ctx):
    """Run tests"""
    ctx.run('poetry run pytest')


@task(test_pytest, test_accept)
def test(ctx):
    """Run tests"""


scm = Collection()
scm.add_task(scm_push, name="push")
scm.add_task(scm_status, name="status")

ns = Collection(build, bumpversion, clean, format, init, lint, release, test, test_accept, test_pytest)
ns.add_collection(scm, name="scm")
