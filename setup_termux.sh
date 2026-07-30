#!/bin/bash

# This script sets up the Termux environment for the Matrix bot and llama-server.

echo "Updating Termux packages..."
pkg update && pkg upgrade -y

echo "Installing necessary packages..."
pkg install -y python python-pip git openssl-tool libcrypt libffi clang rust

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up llama-server (assuming it's already built or will be built manually)..."
echo "Please ensure your llama-server is running on http://127.0.0.1:8080 before starting the bot."
echo "Example command to run llama-server:"
echo "taskset -c 4-7 ./build/bin/llama-server -m ~/Shared/models/gemma-2-2b-it-abliterated-Q4_K_M.gguf -c 2048 -t 4 --no-mmap --port 8080"

echo "
To run the Matrix bot, navigate to the 'termux-bot' directory and execute:
python ribit_termux.py
"

echo "Setup complete!"
