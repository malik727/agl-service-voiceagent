from setuptools import setup, find_packages

packages = [p for p in find_packages()
            if "tests" not in p and "debug" not in p]

setup(
    name="agl_service_voiceagent",
    version="0.3.0",
    description="A gRPC-based voice agent service designed for Automotive Grade Linux (AGL). This service leverages GStreamer, Vosk, Snips, and RASA to seamlessly process user voice commands. It converts spoken words into text, extracts intents from these commands, and performs actions through the Kuksa interface.",
    url="https://github.com/malik727/agl-service-voiceagent",
    author="Malik Talha",
    author_email="talhamalik727x@gmail.com",
    install_requires=[
        "kuksa-client==0.4.0",
        "grpcio>=1.45.0",
        "grpcio-tools>=1.45.0",
        "vosk==0.3.42",
        "PyGObject==3.42.0",
        "rasa==3.6.4",
        "numpy==1.22.3",
        "tensorflow==2.12.0",
        "tensorboard==2.12.0",
        "keras==2.12.0",
    ],
    license="Apache-2.0",
    python_requires=">=3.9",
    packages=packages,
    package_data={'agl_service_voiceagent': ['config.ini']},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "voiceagent-service=agl_service_voiceagent.service:main"
        ],
    }
)