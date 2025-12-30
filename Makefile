# --- Configuration ---
LIB_SOURCE = ./phpython
# Change these if your Mac assigns specific names
PORT = /dev/cu.usbmodem*

.PHONY: deploy clean-local check-platform

# 1. Local Cleanup
clean-local:
	@echo "Cleaning local __pycache__..."
	@find $(LIB_SOURCE) -name "__pycache__" -type d -exec rm -rf {} +
	@find $(LIB_SOURCE) -name "*.pyc" -delete

# 2. Platform Detection
# This checks the internal sys.implementation name via mpremote
detect:
	@echo "Detecting board type..."
	@PLATFORM=$$(mpremote exec "import sys; print(sys.implementation.name)" 2>/dev/null); \
	if [ "$$PLATFORM" = "circuitpython" ]; then \
		echo "Detected: CircuitPython"; \
		make deploy-cp; \
	elif [ "$$PLATFORM" = "micropython" ]; then \
		echo "Detected: MicroPython"; \
		make deploy-mp; \
	else \
		echo "Could not detect platform. Try 'make deploy-mp' or 'make deploy-cp' manually."; \
	fi

# 3. MicroPython Deploy (mpremote)
deploy-mp: clean-local
	@echo "Using mpremote to deploy..."
	-mpremote mkdir :lib
	-mpremote rm -r :lib/phpython
	-mpremote mkdir :lib/phpython
	mpremote cp -r $(LIB_SOURCE)/. :lib/phpython/

# 4. CircuitPython Deploy (ampy)
# Since the drive is read-only, ampy handles the 'backdoor' via serial
deploy-cp: clean-local
	@echo "Using ampy to deploy (USB is Read-Only)..."
	-ampy --port $(PORT) mkdir /lib 2>/dev/null || true
	-ampy --port $(PORT) rmdir /lib/phpython 2>/dev/null || true
	ampy --port $(PORT) put $(LIB_SOURCE) /lib/phpython