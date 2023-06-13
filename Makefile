install:
	./bin/dev/docker-exec.sh poetry install

remove:
	./bin/dev/docker-remove.sh

build:
	./bin/dev/docker-build.sh

build-m1:
	./bin/dev/docker-build-m1.sh

start:
	./bin/dev/docker-start.sh

ssh:
	./bin/dev/docker-ssh.sh

stop:
	./bin/dev/docker-stop.sh

notebook:
	./bin/dev/notebook-start.sh

ipython:
	./bin/dev/ipython-start.sh

server:
	./bin/dev/docker-exec.sh ./bin/dev/webserver-start.sh

curl:
	./bin/dev/curl.sh

lint:
	./bin/dev/docker-exec.sh poetry run black src &&\
	./bin/dev/docker-exec.sh poetry run flake8 --max-line-length=90 src &&\
	./bin/dev/docker-exec.sh poetry run pydocstyle --convention=google &&\
	./bin/dev/docker-exec.sh poetry run mypy --follow-imports=skip \
	--ignore-missing-imports --disallow-untyped-defs

test:
	./bin/dev/docker-exec.sh poetry run pytest -s

kill_streamlit:
	ps aux | grep streamlit | awk '{print $2}' | xargs kill -9

kill_chromium:
	ps -x| grep usr/lib/chromium/chromium | awk '{print $2}' | xargs kill -9

clean_pycache:
	find . -type d -name "__pycache__" -exec rm -rf {} \;

selenium-remove:
	./bin/dev/docker-selenium-remove.sh

selenium-stop:
	./bin/dev/docker-selenium-stop.sh

selenium-start:
	./bin/dev/docker-selenium-start.sh

selenium-backup:
	./bin/dev/docker-selenium-backup.sh

selenium-ssh:
	./bin/dev/docker-selenium-ssh.sh

restart:
	echo "Restarting all:"
	echo "Stopping and restarting selenium docker."
	./bin/dev/docker-selenium-stop.sh
	echo "Wait 5 seconds to give time to the docker to be removed"
	sleep 5
	echo "Restarting selenium docker."
	./bin/dev/docker-selenium-start.sh
	echo "Stopping main docker."
	./bin/dev/docker-stop.sh
	echo "Restarting main container."
	./bin/dev/docker-start.sh
	# echo "Restarting iPython."
	# ./bin/dev/ipython-start.sh
	echo "All done"

sum:
	./bin/dev/docker-exec.sh poetry run dotenv run ipython \
	bin/run/run_sum.py

hello:
	./bin/dev/docker-exec.sh poetry run dotenv run ipython \
	bin/run/run_selenium_hello_world.py

run_whatsapp_send_message_1:
	./bin/dev/docker-exec.sh poetry run dotenv run ipython \
	bin/run/run_whatsapp_send_message.py \
	data/input/contacts1.txt \
	data/input/message1.txt \
	data/input/attachment_image.png \
	data/input/attachment_text.txt


run_whatsapp_send_message_2:
	./bin/dev/docker-exec.sh poetry run dotenv run ipython \
	bin/run/run_whatsapp_send_message.py \
	data/input/contacts2.txt \
	data/input/message2.txt

run_whatsapp_send_message_22:
	./bin/dev/docker-exec.sh poetry run dotenv run ipython \
	bin/run/run_whatsapp_send_message.py \
	data/input/contacts2.txt \
	data/input/message2.txt \
	data/input/attachment_image.png \
	data/input/attachment_text.txt

run_whatsapp_read_messages_3:
	./bin/dev/docker-exec.sh poetry run dotenv run ipython \
	bin/run/run_whatsapp_read_messages.py \
	data/input/contacts3.txt

send:
	make run_whatsapp_send_message_22

read:
	make run_whatsapp_read_messages_3

fix:
	./bin/dev/docker-exec.sh poetry run dotenv run ipython \
	bin/run/run_fixapi.py