# Intro

This project is a template of Docker that reads Whatsapp messages, 
places a trade from them, maybe also uses a FastAPI to record the trades to a backend.

# Steps to set up and test

Create and start the standalone selenium-chromium container based on an image for Arm architecture (M1).
```
make selenium-start
```

Copy the example of these files and modify if needed.
```
cp .bashrc.example .bashrc
cp .env.example .env
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

# Run

Test just that some dummy code runs.
```
./bin/dev/docker-exec.sh poetry run dotenv run ipython bin/run/run_sum.py
```

Or run directly the main script from outside the docker with
```
./bin/dev/docker-exec.sh poetry run dotenv run ipython bin/run/run_selenium_hello_world.py 
```

Send whatsapp messages to a list of contacts, with or without attachments.
```
./bin/dev/docker-exec.sh poetry run dotenv run ipython bin/run/run_whatsapp_send_message.py
```
Or with all arguments
```
./bin/dev/docker-exec.sh poetry run dotenv run ipython bin/run/run_whatsapp_send_message.py data/input/contacts2.txt data/input/message2.txt data/input/attachment_image.png data/input/attachment_text.txt
```
Or in short coded with make
```
make run_whatsapp_send_message_2
```
To read whatsapp messages and parse them to create a trade order object and log them in `./output/order/orders_01.log`:
```
make read | tee a.log
```
This ` | tee a.log` allows the outputs both in the terminal, and in a text file.

To run on a server after ssh to the server and continue to run on the server after I close the laptop or the ssh connection, use `tmux`:
First ssh, then create a session
```
ssh username@server_address
tmux new -s session_name
```
Launch the code on the server
```
make read | tee a.log
```
The detach by running `control+b`, and then `d`. 
You can close laptop, or exit from ssh.
The code will continue to run.
You can log back and check that the log file is being updated. Or log back in to the `tmux` session.
```
ssh username@server_address
tmux attach -t session_name
```