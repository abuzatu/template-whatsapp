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


streamlit_calmcode_simulation:
	./bin/dev/docker-exec.sh ./bin/dev/streamlit-start.sh \
	src/streamlit/tutorial_calmcode/run_simulation.py

streamlit_calmcode_ML:
	./bin/dev/docker-exec.sh ./bin/dev/streamlit-start.sh \
	src/streamlit/tutorial_calmcode/run_ML.py

streamlit_calmcode_pandas:
	./bin/dev/docker-exec.sh ./bin/dev/streamlit-start.sh \
	src/streamlit/tutorial_calmcode/run_pandas.py

streamlit_original_01:
	./bin/dev/docker-exec.sh ./bin/dev/streamlit-start.sh \
	src/streamlit/tutorial_original/run_bokeh_fastapi_01.py

streamlit_original_02:
	./bin/dev/docker-exec.sh ./bin/dev/streamlit-start.sh \
	src/streamlit/tutorial_original/run_bokeh_fastapi_02.py

kill_streamlit:
	ps aux | grep streamlit | awk '{print $2}' | xargs kill -9

kill_chromium:
	ps -x| grep usr/lib/chromium/chromium | awk '{print $2}' | xargs kill -9

clean_pycache:
	find . -type d -name "__pycache__" -exec rm -rf {} \;

chromium-stop:
	./bin/dev/docker-chromium-stop.sh

chromium-start:
	./bin/dev/docker-chromium-start.sh

chromium-ssh:
	./bin/dev/docker-chromium-ssh.sh

restart:
	echo "Restarting all:"
	echo "Stopping chromium docker."
	./bin/dev/docker-chromium-stop.sh
	echo "Restarting chromium docker."
	./bin/dev/docker-chromium-start.sh
	echo "Stopping main docker."
	./bin/dev/docker-stop.sh
	echo "Restarting main container."
	./bin/dev/docker-start.sh
	echo "Restarting iPython."
	./bin/dev/ipython-start.sh
	echo "All done"


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
	data/input/message2.txt \
	data/input/attachment_image.png \
	data/input/attachment_text.txt