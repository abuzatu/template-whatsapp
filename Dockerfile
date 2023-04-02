FROM python:3.11.2-slim-buster

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install curl build-essential libpq-dev openssh-client procps \
    wget gnupg2 unzip sudo \
    less emacs23-nox \
    x11vnc

# ENV SE_VNC_NO_PASSWORD=1
# ENV SE_VNC_VIEW_ONLY=1

# ENV DISPLAY=:1
# EXPOSE 5901

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

# RUN mkdir -p $HOME/.vnc
# RUN touch $HOME/.vnc/passwd
# RUN x11vnc -storepasswd adrian $HOME/.vnc/passwd

COPY --chown=jumbo:jumbo .bashrc $WORKDIR
RUN ln -s $WORKDIR/.bashrc $HOME/.bashrc

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