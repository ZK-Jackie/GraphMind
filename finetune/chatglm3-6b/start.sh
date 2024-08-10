#!/bin/bash
# Fine-tuning of ChatGLMM3 on T2KG dataset

apt update

apt install tmux -y
# Simple usage of tmux:
# 1. new a tmux window, command **on bash** -- tmux new -s <tmux window name>
# 2. quit tmux console environment, actions **on keyboard** -- ctrl+b  d (two seperated movement)
# 3. back to the tmux window, command **on bash** -- tmux attach -t <tmux window name>

apt install python3-mpi4py -y

pip install -r requirements.txt

# start finetune
# python3 finetune_hf.py  /root  /root/chatglm3-6b  lora.yaml