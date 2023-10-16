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
	$(POETRY) run flake8 --max-line-length=96 --exclude storage .

.PHONY: format
format:
	make flake8; make yapf

.PHONY: do-yapf
do-yapf:
	$(POETRY) run yapf -i -r .

.PHONY: test
test:
	$(POETRY) run pytest

.PHONY: coverage
coverage:
	$(POETRY) run pytest --cov-report html:coverage \
		--cov=src \
		tests/
	$(OPEN) coverage/index.html

# From this line, all targets are deprecated and will be removed in the next version
# Use instead:
#
# bin/jan [command]
#
# ...where [command] equals to the following targets:
#
#	Command (and subcommand)	Makefile target
#	 /implemented in Python/
#	-------------------------------------------
#	sys_info local				run_local
#	sys_info remote				run_remote
#	mastodon create_app			create_app
#	mastodon publish_queue		publish_queue
#	mastodon test				publish_test
#	update_ddns					update_ddns
#	listen						listen*
#	scheduler					scheduler
#	git_changes					publish_git_changes
#	
#	Command (and subcommand)	Makefile target
#	 /implemented in bash/
#	-------------------------------------------
#	test_message				test_message
#	listen						listen*
#
.PHONY: run_local
run_local:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	$(POETRY) run python run_local.py

.PHONY: create_app
create_app:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	$(POETRY) run python create_app.py

.PHONY: publish_queue
publish_queue:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	$(POETRY) run python publish_queue.py

.PHONY: publish_test
publish_test:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	$(POETRY) run python publish_test.py

.PHONY: update_ddns
update_ddns:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	$(POETRY) run python update_ddns.py

.PHONY: listen
listen:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	nohup $(POETRY) run python listen.py > log/listen_in_background.log 2>&1 &

.PHONY: background
background:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	ps aux | grep listen.py | grep -v grep
	$(ps aux | grep "[l]isten.py" | awk '{print $2}'); do echo "$pid"; done

.PHONY: kill
kill:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	pkill listen.py

.PHONY: run_remote
run_remote:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	$(POETRY) run python run_remote.py

.PHONY: test_message
test_message:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	curl -X POST -d "hostname=MyHostname&message=This+is+a+test+message" http://localhost:5000/message

.PHONY: scheduler
scheduler:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	$(POETRY) run python scheduler.py

.PHONY: publish_git_changes
publish_git_changes:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	$(POETRY) run python publish_git_changes.py

.PHONY: validate_config
validate_config:
	@echo "\033[1;33mDEPRECATED target: Use bin/jan shell script instead\033[0m"
	@$(PYTHON) -c 'import yaml;yaml.safe_load(open("config.yaml"))' > /dev/null && echo "\033[0;32mThe Config is correct\033[0m" || echo "\033[0;31mThe Config has an error\033[0m"