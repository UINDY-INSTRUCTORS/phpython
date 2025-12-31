# --- Configuration ---
PORT = /dev/cu.usbmodem*
LIB_SOURCE = ./phpython
DEST = /lib/phpython
DEFAULT_SCRIPT = simple_divider.py
BOARD_INFO = board_info.py

# Allow running with: make run foo.py OR make run FILE=foo.py OR just make run
# The first non-target argument becomes the script to run
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
ifneq ($(RUN_ARGS),)
FILE := $(word 1, $(RUN_ARGS))
else
FILE ?= $(DEFAULT_SCRIPT)
endif

.PHONY: deploy reset ls run test clean-local

# 1. Local Cleanup: Removes Mac metadata before sending to the board
clean-local:
	@echo "Cleaning local __pycache__ and .pyc files..."
	@find $(LIB_SOURCE) -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find $(LIB_SOURCE) -name "*.pyc" -delete 2>/dev/null || true

# 2. Universal Deploy: Works for both MP and CP
deploy: clean-local
	@echo "Deploying to board at $(PORT)..."
	-ampy --port $(PORT) mkdir /lib 2>/dev/null || true
	-ampy --port $(PORT) rmdir $(DEST) 2>/dev/null || true
	ampy --port $(PORT) put $(LIB_SOURCE) $(DEST)
	@echo "Deployment successful."

# 3. Hardware Reset: Fixes the 'Invalid State' DAC issue on ESP32
reset:
	@echo "Performing Hardware Reset..."
	-ampy --port $(PORT) run reset_board.py
	@echo "Waiting for board to reboot..."
	@sleep 3

# 4. Universal Run: Executes your experiment
run:
	@echo "Running $(FILE)..."
	ampy --port $(PORT) run $(FILE)

# 5. The "Golden Path": Reset, Deploy, and Run in one shot
all: reset deploy run

# 6. Inspection Helper
ls:
	@echo "Current files in $(DEST):"
	@ampy --port $(PORT) ls $(DEST)

# 4. Universal Run: Executes your experiment
board:
	@echo "Running $(BOARD_INFO)..."
	ampy --port $(PORT) run $(BOARD_INFO)

# Special rule to prevent make from treating .py files as targets
%.py:
	@: