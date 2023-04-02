# Intro

This README file will document the steps needed to build such a Docker and template from scratch, so that it can be used to start later a new project.

# When creating a new project

## .bashrc and .env

Copy the example of these files and modify if needed.
```
cp .bashrc.example .bashrc
cp .env.example .env
```

## Poetry

Usually they say you sould use poetry locally to create the first `pyproject.toml` and `poetry.lock`. But to be really safe and do not get any conflicts with local poetry, we first build the Docker withour these files, just by installing poetry, then we ssh into docker and we run these commands. Any file created inside Docker appears also locally. So we have to comment out some lines. 

In `Dockerfile` comment out
```
# Copy poetry files and install
COPY pyproject.toml poetry.lock $WORKDIR/
RUN poetry install
```

In `bin/make-build` comment out
```
docker exec -i -t $PROJECT_NAME poetry install
```

Build the Docker image
```
make build
```
Start the docker container
```
make start
```
Ssh into the container
```
make ssh
```
Inside you will see like
```
jumbo@f830073bfa07:/opt/app$
```
The `poetry` command is installed, as we can see
```
poetry
```
Create a new poetry environment with
```
poetry init
```
There are some interactive questions like
```
jumbo@f830073bfa07:/opt/app$ poetry init

This command will guide you through creating your pyproject.toml config.

Package name [app]:  
Version [0.1.0]:  
Description []:  template for Docker with FastAPI
Author [None, n to skip]:  Adrian Buzatu
License []:  
Compatible Python versions [^3.11]:  

Would you like to define your main dependencies interactively? (yes/no) [yes] no
Would you like to define your development dependencies interactively? (yes/no) [yes] no
Generated file

[tool.poetry]
name = "app"
version = "0.1.0"
description = "template for Docker with FastAPI"
authors = ["Adrian Buzatu"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"


Do you confirm generation? (yes/no) [yes] yes
```
The result is the creation of a `pyproject.toml` file, which looks like above. To create the `poetry.lock` file run
```
poetry install
```
Exit the ssh with `exit`.

Uncomment in files `Dockerfile` and `bin/docker-start.sh` the two places about `poetry`. 

Remove the image and container with
```
make remove
```
Start again and this time to install `poetry` too.

## Then add packages to poetry

In another tab in the same terminal to
```
make ssh
```
and there add new packages with
```
poetry add numpy
poetry add pandas
poetry add matplotlib
poetry add seaborn
poetry add jupyter
poetry add ipython
poetry add python-dotenv[cli]
```
And so on. This will update `pyproject.toml` and `poetry.lock` and gets them installed, so you can use right away. 

To uninstall a package
```
make remove dotenv
```


# You can run in Jupyter Notebook or iPython or scripts

## dotenv

We use `dotenv` to load the `.env` file (which we do not place in Git) with our environment variables, including API keys that must not be public. This way they are accessible in the scripts. For this we need

```
poetry add python-dotenv[cli]
```

And when running instead of `poetry run` we use `poetry run dotenv run`. The `.env` file looks like this
```
STAGE=DEVELOPMENT
TIMEZONE=UTC

# production example how to include API from a service we use
INPUT_SERVICE_URL = https://input-service.service-provider.io
INPUT_SERVICE_API_KEY = K88dfdkTsdsfd772dfdfd98374k7dGIF

API_KEY=foo
PYTHONPATH=src
LOGGING_LEVEL=DEBUG
```
And we can see that in both `Jupyter Notebook` or `iPython` we can have access to these environment variables with
```
import os
os.environ
```
and the variables appear there, for example
```
In [1]: import os

In [2]: os.environ
Out[2]: 
environ{'PATH': '/home/jumbo/.cache/pypoetry/virtualenvs/app-tq7C0_9c-py3.11/bin:/.local/share/pypoetry/bin/poetry:/home/jumbo/.local/bin:/home/jumbo/.poetry/bin:/home/jumbo/.local/share/pypoetry:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        'HOSTNAME': 'fd222f0cdf41',
        'TERM': 'xterm',
        'LANG': 'C.UTF-8',
        'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D',
        'PYTHON_VERSION': '3.11.2',
        'PYTHON_PIP_VERSION': '22.3.1',
        'PYTHON_SETUPTOOLS_VERSION': '65.5.1',
        'PYTHON_GET_PIP_URL': 'https://github.com/pypa/get-pip/raw/d5cb0afaf23b8520f1bbcfed521017b4a95f5c01/public/get-pip.py',
        'PYTHON_GET_PIP_SHA256': '394be00f13fa1b9aaa47e911bdb59a09c3b2986472130f30aa0bfaf7f3980637',
        'WORKDIR': '/opt/app',
        'PYTHONPATH': 'src',
        'GIT_COMMIT_HASH': '',
        'HOME': '/home/jumbo',
        'VIRTUAL_ENV': '/home/jumbo/.cache/pypoetry/virtualenvs/app-tq7C0_9c-py3.11',
        'STAGE': 'DEVELOPMENT',
        'TIMEZONE': 'UTC',
        'INPUT_SERVICE_URL': 'https://input-service.service-provider.io',
        'INPUT_SERVICE_API_KEY': 'K88dfdkTsdsfd772dfdfd98374k7dGIF',
        'API_KEY': 'foo',
        'LOGGING_LEVEL': 'DEBUG'}

In [3]: 
```


## Jupyter Notebook

For Jupyter Notebook also its port `1335` must be added also in the `bin/docker-start.sh`.

Note though that for `Jupyter Notebook` it worked only after I did rebuilt the image and container. So you exit with
```
exit
```
and from the main repo
```
make remove
make build
make start
```

```
make notebook
```
You will see a message like this
```
./bin/notebook-start.sh
[I 12:11:57.166 NotebookApp] Authentication of /metrics is OFF, since other authentication is disabled.

  _   _          _      _
 | | | |_ __  __| |__ _| |_ ___
 | |_| | '_ \/ _` / _` |  _/ -_)
  \___/| .__/\__,_\__,_|\__\___|
       |_|
                       
Read the migration plan to Notebook 7 to learn about the new features and the actions to take if you are using extensions.

https://jupyter-notebook.readthedocs.io/en/latest/migrate_to_notebook7.html

Please note that updating to Notebook 7 might break some of your extensions.

[W 12:11:57.316 NotebookApp] WARNING: The notebook server is listening on all IP addresses and not using encryption. This is not recommended.
[W 12:11:57.316 NotebookApp] WARNING: The notebook server is listening on all IP addresses and not using authentication. This is highly insecure and not recommended.
[I 12:11:57.318 NotebookApp] Serving notebooks from local directory: /opt/app
[I 12:11:57.318 NotebookApp] Jupyter Notebook 6.5.3 is running at:
[I 12:11:57.318 NotebookApp] http://localhost:1335/
[I 12:11:57.318 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[W 12:11:57.319 NotebookApp] No web browser found: could not locate runnable browser.
```
And now the terminal becomes blocked with the Jupyter Server. You will see printouts here (logs) as you do actions in Jupyter Notebook. You copy the url `http://localhost:1335/`, put it into a browser and then you can use the Notebooks. Note we have a folder `notebooks` where we have the convention to place the Jypyter Notebook files, which have extension `.ipynb`.

## iPython

Interactive Python is lighter and you can develop as in a Jypyter Notebook, but from the terminal. You can run the code up to some point and then continue from there. A huge productivity boost when debugging for tests.

```
make ipython
```

It starts a terminal like this
```
./bin/ipython-start.sh
Python 3.11.2 (main, Mar 17 2023, 02:54:19) [GCC 8.3.0]
Type 'copyright', 'credits' or 'license' for more information
IPython 8.11.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: 
```

You can add lines like this
```
In [1]: import numpy as np

In [2]: 
```
You exit with `Control` + `D`, or type `exit` followed by `Enter`.


## Scripts

Or we can run scripts from the command line with `python`

```
./bin/dev/docker-exec.sh poetry run dotenv run python ./bin/run/run_sum.py
```

or with `ipython`

```
./bin/dev/docker-exec.sh poetry run dotenv run ipython ./bin/run/run_sum.py
```

And these scripts also use the modules we have built.

# Create a new module to use

In the `src` folder we create the folder `utils` that is defined as a Python module by creating inside the file `__init__.py`. Inside the folder we can create several files, like `sum.py` where we create a few functions. `PYTHONPATH` is already set from the `Dockerfile` to `/opt/app/src` folder, so that we can do in Jupyter Notebook `import utils.sum` and then call the function with `utils.sum.my_sum(1.1, 2.2)`. If we need to modify the `PYTHONPATH` later without modifying the docker image, we can do so in the `.env` file.

At the end of include statements we add this 
```
# allow to use an updated module and use the change directly by refreshing the cell
# without having to restart the entire notebook
%load_ext autoreload
%autoreload 2
```
in order to pick up automatically changes in our module and when we rerun the cell, we pick up the changes in Jupyter. That way we do not have to rerun the entire Notebook, or restart Jupyter or rebuilt the image. So very powerful.

# Linting

We first add to poetry
```
poetry add black
poetry add flake8
poetry add pydocstyle
poetry add mypy
```
Then we run 
```
make lint
```
Which in turns runs
```
./bin/docker-exec.sh poetry run black src &&\
./bin/docker-exec.sh poetry run flake8 --max-line-length=90 src &&\
./bin/docker-exec.sh poetry run pydocstyle --convention=google &&\
./bin/docker-exec.sh poetry run mypy --follow-imports=skip --ignore-missing-imports --disallow-untyped-defs
```
Not all this uses the poetry environment and not the local machine poetry.

We can also make checks and transformations every time we run a commit, using th

# GitHub

By using VSCode we can commit to `GitHub` directly from VSCode.