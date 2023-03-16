PYTHON = python3
PIP = pip3

.PHONY: init
init:
	$(PIP) install -r requirements.txt

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

.PHONY: validate_config
validate_config:
	@$(PYTHON) -c 'import yaml;yaml.safe_load(open("config.yaml"))' > /dev/null && echo "\033[0;32mThe Config is correct\033[0m" || echo "\033[0;31mThe Config has an error\033[0m"