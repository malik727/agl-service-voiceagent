# Automotive Grade Linux (AGL) Voice Agent Service
A gRPC-based voice agent service designed for Automotive Grade Linux (AGL). This service leverages GStreamer, Vosk, Snips, and RASA to seamlessly process user voice commands. It converts spoken words into text, extracts intents from these commands, and performs actions through the Kuksa interface.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Maintainers](#maintainers)
- [License](#license)

## Features
- Voice command recognition and execution.
- Support for different Natural Language Understanding (NLU) engines, including Snips and RASA.
- Wake-word detection.
- Easy integration with Kuksa for automotive functionalities.

## Prerequisites
Before you begin, ensure you have met the following requirements:

- Python 3.9 or higher installed on your system.
- The required Python packages and dependencies installed (see [Installation](#installation) section).
- Access to necessary audio and NLU model files (STT, Snips, RASA).
- Kuksa setup if you plan to use automotive functionalities.

## Installation
To install the AGL Voice Agent Service on your local machine, follow these steps:

1. Clone the project repository from GitHub:

   ```bash
   git clone https://github.com/malik727/agl-service-voiceagent.git
   ```
2. Navigate to the project directory.
3. Install dependencies and the voiceagent service package:
   ```bash
   pip install -r requirements.txt
   python setup.py install
   ```

## Usage:
#### Starting the Server
To start the gRPC server, use the following command:

```bash
voiceagent-service run-server
```

You can customize the server behavior by providing additional options such as STT model path, Snips model path, RASA model path, and more. Use the `--help` option to see available options.

To run the server based on the `config.ini` file, simply use the following command:

```bash
voiceagent-service run-server --config
```

This command will automatically configure and start the server using the settings specified in the `config.ini` file. You don't need to provide additional command-line arguments when using this option.

#### Running the Client
To interact with the gRPC server, you can run the client in different modes:
- Wake-word Mode: Detects wake words and triggers voice commands.
- Manual Mode: Manually control voice command recognition.

To run the client in a specific mode, use the following command:

```bash
voiceagent-service run-client --mode MODE --nlu NLU_ENGINE
```
Replace MODE with the desired mode (e.g., "wake-word") and NLU_ENGINE with the preferred NLU engine (e.g., "snips").

## Configuration
Configuration options for the AGL Voice Agent Service can be found in the `config.ini` file. You can customize various settings, including the service version, audio directories, and Kuksa integration. **Important:** while manually making changes to the config file make sure you add trailing slash to all the directory paths, ie. the paths to directories should always end with a `/`. 

## Maintainers
- **Malik Talha** <talhamalik727x@gmail.com>

## License
This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.