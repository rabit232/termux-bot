# Termux Matrix Bot (Ribit 2.0)

This repository contains a Matrix bot designed to run on Android via Termux, utilizing a local LLM served by `llama-server`.

## Features
- **Local LLM Integration**: Connects to `llama-server` running on localhost.
- **Matrix Protocol**: Uses `matrix-nio` for communication.
- **Command System**: Supports `?ask`, `?sys`, `?status`, and `?open`.
- **Emotional Intelligence**: Built-in emotional response system.
- **Security**: Authorized user list for system commands.

## Setup Instructions

### 1. Install Dependencies in Termux
Run the provided setup script:
```bash
chmod +x setup_termux.sh
./setup_termux.sh
```

### 2. Start llama-server
Start your local model server in a separate Termux session or tab:
```bash
taskset -c 4-7 ./build/bin/llama-server -m ~/Shared/models/gemma-2-2b-it-abliterated-Q4_K_M.gguf -c 2048 -t 4 --no-mmap --port 8080
```

### 3. Configure the Bot
The bot is pre-configured with the following credentials:
- **Homeserver**: `https://matrix.stargazypie.xyz`
- **User ID**: `@merkaba:stargazypie.xyz`
- **Password**: `d3rLl2UrTAmeGb`

You can modify these in `ribit_termux.py` if needed.

### 4. Run the Bot
```bash
python ribit_termux.py
```

## Commands
- `?ask [question]`: Query the local LLM.
- `?sys`: Get Termux system status (CPU/RAM).
- `?open [app]`: Open an application on Termux.
- `?help`: Show available commands.
- `?play_youtube [url]`: Play a YouTube video.

## Authorized Users
Only the following users are authorized for system commands:
- `@merkaba:stargazypie.xyz`
- `@ribit:envs.net`
- `@rabit232:envs.net`

## Credits
Based on the Ribit 2.0 project by [rabit232](https://github.com/rabit232).
