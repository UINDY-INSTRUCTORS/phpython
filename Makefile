# Variables
PORT = /dev/cu.usbmodem* # Adjust if your Mac uses a different name
LIB_SOURCE = ./phpython
DEV_DEST = :lib/phpython

.PHONY: reset deploy run experiment clean

# 1. Hard reset the board and wait for it to come back
reset:
	@echo "Hard resetting ESP32-S2..."
	-mpremote run reset_board.py
	@sleep 3

# 2. Deploy your library (Removes old version first to avoid conflicts)
# Point directly to the source folder in your root
deploy:
	@echo "Cleaning local cache..."
	-find $(LIB_SOURCE) -name "__pycache__" -type d -exec rm -rf {} +
	-find $(LIB_SOURCE) -name "*.pyc" -delete
	@echo "Deploying lean source to $(DEV_DEST)..."
	-mpremote mkdir :lib
	-mpremote rm -r $(DEV_DEST)
	-mpremote mkdir $(DEV_DEST)
	mpremote cp -r $(LIB_SOURCE)/. $(DEV_DEST)/

# 3. Run the specific experiment script
run:
	@echo "Starting experiment..."
	mpremote run starter_micro.py

# 4. The "Golden Chain": Reset, Deploy, and Run in one go
all: reset deploy run

# 5. Quick helper to see what's on the board
ls:
	mpremote ls :lib/