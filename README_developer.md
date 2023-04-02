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

# Selenium and chrome driver

When running locally on a Mac, we install the appropriate Chrome driver and add it to `/usr/local/bin/chromedriver`, and install `selenium` via `poetry` or `pip install`. The goal of this project is to run in a `Docker` container. `selenium` is installed via `poetry`, but for `google-chrome` browser and the `chrome-driver` there are particularities for the M1 laptops. Google does not build these for the Arm architecture that M1 uses. 

## For Linux (AMD) and Mac with Intel processors

I have found documentation online, added to Dockerfile and checked that it works indeed on an Intel M1. Change these to Dockerfile. 

Install a few more linux libraries that are needed and install `google-chrome`. 
```
USER root
RUN apt-get install -y wget gnupg2 unzip sudo
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# RUN sudo apt-get -y update
# RUN sudo apt-get install -y google-chrome-stable
```

Then set up `ChromeDriver`
```
# Set up ChromeDriver
RUN LATEST=`curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/
```
With these you only need one Dockerfile. 

Documentation on these steps you can find at this [https://www.reddit.com/r/docker/comments/vhys64/running_selenium_with_chromedriver_via_docker_on/](Reddit post).

For Whatsapp to not have to scan every time, you create a new profile folder in your Docker.
```
mkdir -p /home/jumbo/.config/google-chrome/Whatsapp
```

## For Mac laptops of type M1

The method above did not work for M1. `make build` would fail. If we used `make build-m1`, it would not fail, but it would fail in `ipython` or `Jupyter Notebook` when we create the `driver` object, even if pointing to the right path of the `chromedriver` locally. The libraries are not compative with M1.

The solution is to use a second second container from the image `seleniarm` for `standalone-chromium`. Note `arm` for the M1 processor. `Chromium` is the open source platform on which `Chrome` is built, also from Google. Basically it is like a `Chrome` browser. We build a container based on this image. The selenium does not offer for M1, but the selenium community fork from it and create for M1 and offer the image. Its [Chromedriver is here](https://chromedriver.chromium.org/downloads). The [https://www.browserstack.com/guide/difference-between-chrome-and-chromium](differences between Chrome and Chromium) explained here.

We start this container (which will also download the image), as explained by [https://github.com/seleniumhq-community/docker-seleniarm](GitHub.com/SeleniumHQ-Community/docker-seleriarm), to which we add `-d` (detached mode, to give us back access to terminal) and create a name of the container by adding `--name standalone-chromium` (to be used later to link it into our `template-whatsapp` container) 
```
docker run --rm -it -d -p 4444:4444 -p 5900:5900 -p 7900:7900 --name standalone-chromium --shm-size 2g seleniarm/standalone-chromium:latest
```
The original instruction was this
```
docker run --rm -it -p 4444:4444 -p 5900:5900 -p 7900:7900 --shm-size 2g seleniarm/standalone-chromium:latest
```
A [https://www.youtube.com/watch?v=rAia60kxth8](Youtube video) that explains these steps is here. Also a [https://stackoverflow.com/questions/66478751/seleniumwebdrivererror-chrome-crashed-on-m1-chip](StackOverflow) post, and in a [https://github.com/SeleniumHQ/selenium/issues/9733](Docker post). And about XServer also explained in a [https://thespecguy.medium.com/launching-google-chrome-on-docker-container-a7dc2ba2d5](Medium post).

Then ssh into the container
```
docker exec -i -t standalone-chromium /bin/bash
```
To not have to scan `Whatsapp` at every login, create a folder to remind the `Whatsapp` profile, and we will use this folder in our code when we open the `chromedriver`.
```
mkdir -p /home/seluser/.config/chromium/google-chrome/Whatsapp
```
But you can create also from the outside 
```
docker exec -i -t standalone-chromium mkdir -p /home/seluser/.config/chromium/google-chrome/Whatsapp
```
Already at start, it has these processes open, if you check `ps -x` from the Terminal (you can do from Docker Desktop too)
```
$ ps -x
  PID TTY      STAT   TIME COMMAND
    1 pts/0    Ss+    0:00 bash /opt/bin/entry_point.sh
    8 pts/0    S+     0:00 /usr/bin/python3 /usr/bin/supervisord --configuration /etc/supervisord.conf
   15 pts/0    S      0:00 bash /opt/bin/start-xvfb.sh
   16 pts/0    S      0:00 bash /opt/bin/start-vnc.sh
   18 pts/0    S      0:00 bash /opt/bin/start-novnc.sh
   20 pts/0    S      0:00 /bin/sh /usr/bin/xvfb-run --server-num=99 --listen-tcp --server-args=-screen 0 1360x1020x24 -fbdir /var/tmp -dpi 96 -li
   21 pts/0    S      0:00 bash -c /opt/bin/start-selenium-standalone.sh; EXIT_CODE=$?; kill -s SIGINT `cat /var/run/supervisor/supervisord.pid`; 
   23 pts/0    S      0:00 bash /opt/bin/noVNC/utils/novnc_proxy --listen 7900 --vnc localhost:5900
   29 pts/0    S      0:00 bash /opt/bin/start-selenium-standalone.sh
   46 pts/0    S      0:00 python3 -m websockify --web /opt/bin/noVNC/utils/../ 7900 localhost:5900
   50 pts/0    Sl     0:00 Xvfb :99 -screen 0 1360x1020x24 -fbdir /var/tmp -dpi 96 -listen tcp -noreset -ac +extension RANDR -auth /tmp/xvfb-run.F
   78 pts/0    S      0:01 /usr/bin/fluxbox -display :99.0
   85 pts/0    Sl     0:03 java -Dwebdriver.http.factory=jdk-http-client -jar /opt/selenium/selenium-server.jar --ext /opt/selenium/selenium-http-
  135 pts/0    S      0:00 x11vnc -usepw -forever -shared -rfbport 5900 -rfbportv6 5900 -display :99.0
  136 pts/1    Ss     0:00 /bin/sh
  142 pts/1    R+     0:00 ps -x
$ 
```


To find the IP of this container
```
docker inspect standalone-chromium
```
To look at logs created in docker while building and after
```
docker logs standalone-chromium
```

We link this second container to our main container `template-whatsapp` in `./bin/dev/docker-start.sh`
```
        --link standalone-chromium \
```

We can test all the steps with
```
poetry run dotenv run ipython bin/run/run_selenium_hello_world.py
```
Or to be more visual, start `ipython` with 
```
make ipython
```
and paste there the content of `run_selenium_hello_world.py` as here.

Note that sometimes it takes several minutes for the `driver` object to be built and sometimes it is fast, but also can lead to timeouts.
```
"""Module to run in one go the selenium hello world."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

print("test01")
# CHROME_PROFILE_PATH="user-data-dir=$HOME/.config/google-chrome/Whatsapp"
CHROME_PROFILE_PATH = (
    "user-data-dir=/home/seluser/.config/chromium/google-chrome/Whatsapp"
)
# remove Default from below and replace with our new folder called "Whatsapp"
# MacOS: /Users/abuzatu/Library/Application Support/Google/Chrome/Default
# Linux: home/abuzatu/.config/google-chrome/default

print("test02")
# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument('--headless') # Commented out
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(CHROME_PROFILE_PATH)

print("test03")
# Start ChromeDriver
driver = webdriver.Remote(
    command_executor="http://standalone-chromium:4444/wd/hub", options=chrome_options
)
print("test04")
driver.maximize_window()

driver.get("https://www.google.com")
print("test05")
time.sleep(5)

driver.get("https://www.hotnews.ro/sport")
print("test06")
time.sleep(5)

driver.get("https://web.whatsapp.com")
print("test07")
time.sleep(30)

print("test08")
```

A hello world to query the first page at google is on [https://stackoverflow.com/questions/59482607/how-can-i-use-selenium-python-to-do-a-google-search-and-then-open-the-results](StackOverflow). It did not work for me as first it asks to accept some cookies, so you can not search Google directly.

Another example here on [https://stackoverflow.com/questions/61805008/using-selenium-standalone-chrome-in-docker-compose-connecting-with-pythons-sele](StackOverflow), including `docker compose` between the container of standalone selenium and the docker with Python.

### Monitor the webdriver from the outside 

From our local machine we want to monitor and interacted with the webdriver. Below is what I tried, and some sources I studied. Main reference is the [https://github.com/SeleniumHQ/docker-selenium#debugging](README.md) of `SeleniumHQ/docker-selenium` on `Debugging`, as it is for Debugging that we connect from the localmachine to the webserver inside. 

#### What worked for me

What worked was the version without `VNC`, so going to the brower and typing [http://localhost:7900](http://localhost:7900), then setting the password `secret`. Also you can check the sessions that exist here [http://localhost:4444/ui#/sessions](http://localhost:4444/ui#/sessions). If using `VNC` see below, it should be here [http://localhost:5900](http://localhost:5900), but it did not work for me.

#### What did not work for me.

We can do that via the `vncviewer` software, but in the end it did not work. Here are some things I tried for future reference if we want to try it.

Documentation about the [https://wiki.archlinux.org/title/x11vnc](x11vnc).

On local machine install [https://tigervnc.org](TigerVNC).
```
brew install tiger-vnc
```

Then start `vncviewer` and giving it the password `adrian` set in the Docker container.
```
vncviewer -SecurityTypes VncAuth -passwd <<< "adrian" localhost:5901
```
Maybe to try port 5900 instead?
Other trials from other documentation online
```
vncserver :1 -geometry 1280x800 -depth 24
vncviewer localhost:5901
open vnc://localhost:5901
```
Could be related to needing this
```
docker run -d -p 4444:4444 -p 5900:5900 selenium/standalone-chrome-debug
```



