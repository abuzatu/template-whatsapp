FROM python:3.11.2-slim-buster

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install curl build-essential libpq-dev openssh-client procps \
    # less wget gnupg2 unzip sudo \
    emacs23-nox \
    #tigervnc-standalone-server \
    #xfce4 xfce4-terminal \
    #&& rm -rf /var/lib/apt/lists/*
    # build-dep x11vnc
    x11vnc

ENV SE_VNC_NO_PASSWORD=1
ENV SE_VNC_VIEW_ONLY=1

ENV DISPLAY=:1
EXPOSE 5901

#USER root
# Setup key with
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# Setup repository with
#RUN sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
# RUN sh -c 'echo "deb [arch=arm64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
# RUN sh -c 'echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'


#RUN apt-get install -y wget gnupg2 unzip
#RUN echo "ADRIAN"
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN echo "ADRIAN2"
#RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
#RUN less /etc/apt/sources.list.d/google.list
#RUN echo "ADRIAN3"
#RUN sudo apt-get update -y
#RUN sudo apt-cache search google-chrome-stable
#RUN sudo apt-get install -y google-chrome-stable
#RUN echo "ADRIAN4"
#RUN CHROMEVERADI=$(google-chrome --product-version | grep -o "[^\.]*\.[^\.]*\.[^\.]*")
#RUN echo "ADRIAN4_${CHROMEVERADI}"
#RUN CHROMEVER=$(google-chrome --product-version | grep -o "[^\.]*\.[^\.]*\.[^\.]*") && \
#    DRIVERVER=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMEVER") && \
#   wget -q --continue -P /chromedriver "http://chromedriver.storage.googleapis.com/$DRIVERVER/chromedriver_linux64.zip" && \
#    unzip /chromedriver/chromedriver* -d /chromedriver

# install google chrome
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# RUN sudo apt-get -y update
# RUN sudo apt-get install -y google-chrome-stable


#RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
#    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
#    apt-get update && \
#    apt-get install -y google-chrome

# Add Chrome repository
# RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
#   wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -


# Install Chrome
# RUN apt-get update && apt-get install -y google-chrome-stable

# Set up ChromeDriver
#RUN LATEST=`curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
#    wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip && \
#    unzip chromedriver_linux64.zip && \
#    rm chromedriver_linux64.zip && \
#    mv chromedriver /usr/local/bin/

ENV WORKDIR /opt/template-whatsapp
ENV PYTHONPATH $PYTHONPATH:$WORKDIR/src
WORKDIR $WORKDIR

RUN groupadd --gid 1000 jumbo && \
    adduser --system jumbo --uid 1000 --gid 1000 && \
    echo 'jumbo:mypassword' | chpasswd && \
    chown -R jumbo:jumbo $WORKDIR
RUN echo 'jumbo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER jumbo
ENV HOME=/home/jumbo

RUN mkdir -p $HOME/.vnc
RUN touch $HOME/.vnc/passwd
RUN x11vnc -storepasswd adrian $HOME/.vnc/passwd

COPY --chown=jumbo:jumbo .bashrc $WORKDIR
RUN ln -s $WORKDIR/.bashrc $HOME/.bashrc

# Download and install chromedriver
#RUN LATEST=`curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
#    wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip && \
#    unzip chromedriver_linux64.zip && \
#    rm chromedriver_linux64.zip && \
#    mv chromedriver /usr/local/bin/

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/.local/share/pypoetry/bin/poetry:/home/jumbo/.local/bin:/home/jumbo/.poetry/bin:/home/jumbo/.local/share/pypoetry:${PATH}"

# Copy poetry files and install
COPY pyproject.toml poetry.lock $WORKDIR/
RUN poetry config installer.modern-installation false
# RUN poetry run pip install debugpy
RUN poetry install

# use Dockerignore
COPY --chown=jumbo:jumbo . $WORKDIR

ARG GIT_COMMIT_HASH
ENV GIT_COMMIT_HASH=${GIT_COMMIT_HASH}