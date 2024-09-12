#!/bin/bash
# Fine-tuning of ChatGLMM3 on T2KG dataset

apt update

apt install tmux -y
# Simple usage of tmux:
# 1. new a tmux window, command **on bash** -- tmux new -s <tmux window name>
# 2. quit tmux console environment, actions **on keyboard** -- ctrl+b  d (two seperated movement)
# 3. back to the tmux window, command **on bash** -- tmux attach -t <tmux window name>

python -m pip install --upgeade pip

pip install -r requirements.txt

# choose to fix opencv or not
# python -c "from opencv_fixer import AutoFix; AutoFix()"

# start finetune
# xtuner train qwen1_5_14b_chat_qlora_t2kg_e3_0116.py --deepspeed deepspeed_zero2