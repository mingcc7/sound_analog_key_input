# Sound analog key input

## Introduction

Each voice input multiple audio (100 recommended), as a data set for model training, binding device input keys, so that the generated model to monitor each voice forecast, the result of the binding keys for analog input.

## Question

1.An error occurs when a sound is played: The specified device is not turned on or is not recognized by the MCI.
Navigate to the playsound.py file that reported the error and remove.encode('utf-16') after command = '.join(command).encode('utf-16').