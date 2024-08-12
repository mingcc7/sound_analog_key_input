# Sound analog key input

## Introduction

Each voice input multiple audio, as a data set for model training, binding device input keys, so that the generation model to monitor each voice forecast, the result of the binding key for analog input.

## Installation

### conda creates the environment

conda create -n sound_analog_key_input python=3.8

### Activate the environment

conda activate sound_analog_key_input

### Enter the project path

cd sound_analog_key_input

### Install dependency packages

pip install -r requirements.txt

### Run the project

python sound_analog_key_input.py

### Package as exe and compress, file in dist path

python pack_exe.py