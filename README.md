---
frameworks:
- PyTorch

license: Apache License 2.0

tasks:
- relation-extraction

model-type:
- InternLM-20b-chat

domain:
- NLP

tags:
- Fine-tune
---


> <div style="margin: auto; text-align: center;" align="center"><h1>ChatKG<br/>Chat with & Build Your Personal Knowledge Graph </h1><p  style="text-align: center;">ZK-Jackie  2024.3.16</p></div>

<div style="display: flex; align-items: center; justify-content: center;" align="center">
    <a href="https://github.com/ZK-Jackie/ChatKG/blob/main/LICENSE">
        <img src="https://raw.githubusercontent.com/ZK-Jackie/llm_study/master/assests/License-Apache--2.0-green.svg" alt="license" height="20px">
    </a>
</div>
<div style="display: flex; align-items: center; justify-content: center; height: 50px;" align="center">
    <a href="https://www.modelscope.cn/models/Jackie101/ChatKG_InternLM" style="border-right: 1px solid lightgray; padding-right: 10px; margin-right: 10px; height: 30px; display: flex; align-items: center; justify-content: center;">
    <img src="https://raw.githubusercontent.com/ZK-Jackie/llm_study/master/assests/modelscope-logo.svg" alt="modelscope" height="20px">
    </a>
    <a href="https://huggingface.co/ZK-Jackie/ChatKG_InternLM" style="border-right: 1px solid lightgray; padding-right: 10px; margin-right: 10px; height: 30px; display: flex; align-items: center; justify-content: center;">
        <img src="https://raw.githubusercontent.com/ZK-Jackie/llm_study/master/assests/hf-logo-large.png" alt="huggingface" height="30px">
    </a>
    <a href="https://github.com/InternLM/Tutorial/tree/camp3" style="display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 18px; color: rgb(27,56,130); height: 30px;">
        <img src="https://raw.githubusercontent.com/ZK-Jackie/llm_study/master/assests/internlm-logo.svg" alt="internlm" height="30px"/> Tutorial
    </a>
    <a href="https://github.com/ZK-Jackie/ChatKG/blob/main/LICENSE" style="border-left: 1px solid lightgray; padding-left: 10px; margin-left: 10px; height: 30px; display: flex; align-items: center; justify-content: center;">
        <img src="https://raw.githubusercontent.com/ZK-Jackie/llm_study/master/assests/openxlab-models.svg" alt="openxlab" height="20px">
    </a>
</div>
<div style="display: flex; align-items: center; justify-content: center; height: 50px;" align="center">
        English
    <a href="javascript:void(0)" style="border-left: 1px solid lightgray; padding-left: 10px; margin-left: 10px;">
        中文
    </a>
</div>

## Introduction 📖 
ChatKG is a LLM application and a intelligent agent based on InternLM and LangChain, devoted to the construction of personal knowledge graph.

- Constructing Personal KG
  - Understand the meaning of the paragraph
  - Build a personal knowledge graph based on the information users provide
  - Visualize and show the knowledge graph

- Chat with users
  - Answer questions based on the knowledge graph
  - Chat with users and answer questions based on the knowledge graph
  - ...

## Features 🌟
- based on InternLM-chat-7b（Update to InternLM2 lately）
- Multi-modal Chat with users
- Highly customizable

## Demo 🎥
demo is coming soon...

## Developing Timeline ⏲️
- [2024.7.12] The project is reactivated, and will join the InternLM training camp Ⅲ project.
- [2024.4.16] Due to the recent busy academic study, the development of this project has been suspended, and the restart time is unknown...
- [2024.3.14] T2KG Dataset prepared, extracting fine-tuning start.
- [2024.3.12] Start the project.

## Quick Start 🚀
Firstly, configuration in file `config.py` can be modified according to your needs or local computer environment. The flexible configuration:

| Parameter             | Type | Default Value            |
|-----------------------| --- |--------------------------|
| LLM Model Path        | str | `huggingface repo id`    |
| Chat Function         | bool | `True`                   |
| Knowledge Graph Cache | str | `kg`                     |
| Neo4j Bolt URL        | str | `bolt://localhost:7474/` |
| Neo4j Username        | str | `neo4j`                  |
| Neo4j Password        | str | `chatkg666`              |

There are two ways to use ChatKG:

- Try ChatKG on OpenXLab (in the future)


- Run ChatKG on your local machine

**Step 1: Clone the repository**
```bash
git clone https://github.com/ZK-Jackie/ChatKG.git
cd ChatKG
```

**Step 2: Install the dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Run the ChatKG**
```bash
python app.py
```

**Step 4: Open the browser and visit the following URL**
```bash
http://localhost:7860/
```

Besides, it is worth mentioning that running *ChatKG* locally means you need to download and load the LLM model and the knowledge graph data.

The model and knowledge graph data is not included in the repository and running it locally requires a lot of hardware resources, here is the minimum hardware requirements:
- GPU: 1/4 A100
- CPU: 8-core
- Memory: 16G
- Disk: 30G


## Structure 🏗️
```text
tree
.
├─assets
├─chat
├─kg
└─rag
```

## License 📜
This project is released under the [Apache License 2.0](LICENSE). Please also adhere to the Licenses of models and datasets being used.

## Contact 📧
If you have any questions, please contact me at [EMAIL](mailto:jackiey101@foxmail.com)

## Reference 📚

This project uses information from the following sources:

- [XTuner: A Toolkit for Efficiently Fine-tuning LLM](https://github.com/InternLM/xtuner)
- [InternLM: A Multilingual Language Model with Progressively Enhanced Capabilities](https://github.com/InternLM/InternLM)
- [QAMedicalKG: 基于医疗知识图谱自动问答](https://gitee.com/zhangdadao/QAMedicalKG)
- [ollama_knowlage_graph: 使用 LLM，将任何文本语料库转化为知识图谱](https://github.com/mcks2000/llm_notebooks/tree/main/ollama_knowlage_graph)
- [T2KG(pre-release)](https://www.modelscope.cn/datasets/Jackie101/T2KG)
- [书生大模型实战营](https://github.com/InternLM/Tutorial)

## Acknowledgement 🙏

**Special thanks to Shanghai Artificial Intelligence Laboratory for its support of this project.**

