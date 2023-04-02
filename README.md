# Intro

This project is a template of Docker that reads Whatsapp messages, 
places a trade from them, maybe also uses a FastAPI to record the trades to a backend.

# Steps

Create and start the standalone selenium-chromium container based on an image for Arm architecture (M1).
```
make selenium-start
```

Build our own docker image. For this we should not use the M1 version.
```
make build
```
Start the container
```
make start
```
Start `ipython`
```
make ipython
```
Or jupyter notebook
```
make notebook
```
And test selenium and whatsapp by pasting the content of `run/bin/run_selenium_hello_world.py`