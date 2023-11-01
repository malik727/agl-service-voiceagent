# Automotive Grade Linux (AGL) Voice Agent Service
A gRPC-based voice agent service designed for Automotive Grade Linux (AGL). This service leverages GStreamer, Vosk, Snips, and RASA to seamlessly process user voice commands. It converts spoken words into text, extracts intents from these commands, and performs actions through the Kuksa interface.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
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

- AGL master branch (or later) installed on your target device.
- `meta-offline-voice-agent` layer added to your AGL build.
- Access to necessary audio and NLU model files (STT, Snips, RASA).
- Kuksa setup if you plan to use automotive functionalities.

## Usage:
#### Starting the Server
To start the gRPC server, use the following command:

```bash
voiceagent-service run-server
```

You can customize the server behavior by providing additional options such as STT model path, Snips model path, RASA model path, and more. Use the `--help` option to see available options.

To run the server based on the default config file, simply use the following command:

```bash
voiceagent-service run-server --default
```

This command will automatically configure and start the server using the settings specified in the default file. You don't need to provide additional command-line arguments when using this option.

Or, you can manually specify the config file path using the `--config` option:

```bash
voiceagent-service run-server --config CONFIG_FILE_PATH
```   

#### Running the Client
To interact with the gRPC server, you can run the client in different modes:
- Wake-word Mode: Detects wake words and triggers voice commands.
- Manual Mode: Manually control voice command recognition.

To run the client in a Wake-word mode, use the following command:
```bash
voiceagent-service run-client --server_address SERVER_IP --server_port SERVER_PORT --mode wake-word
```
Replace `SERVER_IP` with IP address of the running Voice Agent server, and `SERVER_PORT` with the port of the running Voice Agent server.

To run the client in Manual mode, use the following command:
```bash
voiceagent-service run-client --server_address SERVER_IP --server_port SERVER_PORT --mode manual --nlu NLU_ENGINE
```
Replace `NLU_ENGINE` with the preferred NLU engine ("snips" or "rasa"), `SERVER_IP` with IP address of the running Voice Agent server, and `SERVER_PORT` with the port of the running Voice Agent server. You can also pass a custom value to flag `--recording-time` if you want to change the default recording time from 5 seconds to any other value.

## Configuration
Configuration options for the AGL Voice Agent Service can be found in the default `config.ini` file. You can customize various settings, including the AI models, audio directories, and Kuksa integration. **Important:** while manually making changes to the config file make sure you add trailing slash to all the directory paths, ie. the paths to directories should always end with a `/`. 

## Maintainers
- **Malik Talha** <talhamalik727x@gmail.com>

## License
This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.