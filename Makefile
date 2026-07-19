.DEFAULT_GOAL := help

CACHE_DIR        := .cache/accounts
ENV_FILE         := .env
FIREFOX_PID_FILE := .cache/firefox.pid
FIREFOX_CMD_FILE := .cache/firefox_daemon.cmd
FIREFOX_LOG_FILE := .cache/firefox_daemon.log

.PHONY: help install scrape download all setup shutdown clean

help:
	@echo "Available commands:"
	@echo "  make install                Install Python dependencies"
	@echo "  make scrape                 Scrape video links from the X media tab"
	@echo "  make download               Download videos from scraped links"
	@echo "  make all                    Scrape then download"
	@echo "  make setup [ACCOUNT=name]   Open Firefox with the auto-detected profile and leave it running;"
	@echo "                              with ACCOUNT=name, also points the scraper at X account 'name'"
	@echo "                              (caches the previous account's .env so switching back is instant)."
	@echo "                              If Firefox is already open, re-runs just navigate it to the new"
	@echo "                              account's page instead of starting a second Firefox process."
	@echo "  make shutdown               Close the Firefox opened by 'make setup' and delete cached account snapshots"
	@echo "  make clean                  Remove Python bytecode caches"

install:
	pip install -r requirements.txt

scrape:
	python src/xcrapping_video_links.py

download:
	python src/dling_videos_from_links.py

all: scrape download

setup:
	@mkdir -p $(CACHE_DIR)
	@[ -f $(ENV_FILE) ] || cp .env.example $(ENV_FILE)
	@if [ -n "$(ACCOUNT)" ]; then \
		current=$$(grep '^X_USERNAME=' $(ENV_FILE) | cut -d= -f2-); \
		if [ -n "$$current" ]; then \
			cp $(ENV_FILE) $(CACHE_DIR)/$$current.env; \
			echo "Cached .env for $$current"; \
		fi; \
		if [ -f $(CACHE_DIR)/$(ACCOUNT).env ]; then \
			cp $(CACHE_DIR)/$(ACCOUNT).env $(ENV_FILE); \
			echo "Restored cached .env for $(ACCOUNT)"; \
		elif grep -q '^X_USERNAME=' $(ENV_FILE); then \
			sed -i "s/^X_USERNAME=.*/X_USERNAME=$(ACCOUNT)/" $(ENV_FILE); \
			echo "Switched X_USERNAME to $(ACCOUNT)"; \
		else \
			echo "X_USERNAME=$(ACCOUNT)" >> $(ENV_FILE); \
			echo "Set X_USERNAME to $(ACCOUNT)"; \
		fi; \
	fi
	@account=$$(grep '^X_USERNAME=' $(ENV_FILE) | cut -d= -f2-); \
	url="https://x.com/$$account/media"; \
	if [ -f $(FIREFOX_PID_FILE) ] && kill -0 "$$(cat $(FIREFOX_PID_FILE))" 2>/dev/null; then \
		echo "$$url" > $(FIREFOX_CMD_FILE); \
		echo "Firefox already open (pid $$(cat $(FIREFOX_PID_FILE))) - switched to $$url"; \
	else \
		nohup python src/firefox_daemon.py "$$url" >$(FIREFOX_LOG_FILE) 2>&1 & \
		echo $$! > $(FIREFOX_PID_FILE); \
		echo "Firefox launched at $$url (pid $$(cat $(FIREFOX_PID_FILE))) - stays open until 'make shutdown'"; \
	fi

shutdown:
	@if [ -f $(FIREFOX_PID_FILE) ]; then \
		pid=$$(cat $(FIREFOX_PID_FILE)); \
		if kill -0 "$$pid" 2>/dev/null; then \
			echo "__QUIT__" > $(FIREFOX_CMD_FILE); \
			for i in 1 2 3 4 5 6 7 8 9 10; do \
				kill -0 "$$pid" 2>/dev/null || break; \
				sleep 1; \
			done; \
			if kill -0 "$$pid" 2>/dev/null; then \
				kill "$$pid" 2>/dev/null; \
				echo "Firefox did not exit cleanly in time, force-killed (pid $$pid)"; \
			else \
				echo "Closed Firefox (pid $$pid)"; \
			fi; \
		fi; \
		rm -f $(FIREFOX_PID_FILE) $(FIREFOX_CMD_FILE); \
	fi
	rm -rf $(CACHE_DIR)
	@echo "Removed cached account snapshots ($(CACHE_DIR))"

clean:
	rm -rf src/__pycache__ firefox_tmp_profile
