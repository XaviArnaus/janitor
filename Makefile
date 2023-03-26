PYTHON = python3
POETRY ?= poetry

ifeq ($(OS), Darwin)
	OPEN := open
else
	OPEN := xdg-open
endif

.PHONY: init
init:
	$(POETRY) install

.PHONY: yapf
yapf:
	$(POETRY) run yapf -r --diff .

.PHONY: flake8
flake8:
	$(POETRY) run flake8 . \
		--select=E9,F63,F7,F82 \
		--show-source \
		--statistics
	# Full linter run.
	$(POETRY) run flake8 --max-line-length=96 .

.PHONY: format
format:
	make flake8; make yapf

.PHONY: test
test:
	$(POETRY) run pytest

.PHONY: coverage
coverage:
	$(POETRY) run pytest --cov-report html:coverage \
		--cov=src \
		tests/
	$(OPEN) coverage/index.html

.PHONY: run_local
run_local:
	$(PYTHON) run_local.py

.PHONY: create_app
create_app:
	$(PYTHON) create_app.py

.PHONY: publish_queue
publish_queue:
	$(PYTHON) publish_queue.py

.PHONY: listen
listen:
	nohup $(PYTHON) listen.py > log/listen_in_background.log 2>&1 &

.PHONY: background
background:
	ps aux | grep listen.py | grep -v grep
	$(ps aux | grep "[l]isten.py" | awk '{print $2}'); do echo "$pid"; done

.PHONY: kill
kill:
	pkill listen.py

.PHONY: run_remote
run_remote:
	$(PYTHON) run_remote.py

.PHONY: test_message
test_message:
	curl -X POST -d "hostname=MyHostname&message=This+is+a+test+message" http://localhost:5000/message

.PHONY: scheduler
scheduler:
	$(PYTHON) scheduler.py

.PHONY: validate_config
validate_config:
	@$(PYTHON) -c 'import yaml;yaml.safe_load(open("config.yaml"))' > /dev/null && echo "\033[0;32mThe Config is correct\033[0m" || echo "\033[0;31mThe Config has an error\033[0m"