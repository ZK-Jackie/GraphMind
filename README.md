> <div align="center"><h1>ChatKG<br/>Chat with & Build Your Personal Knowledge Graph </h1><p  style="text-align: center;">ZK-Jackie  2024.3.16</p></div>

[![license](./assets/license.svg)](https://github.com/ZK-Jackie/ChatKG/blob/main/LICENSE) |
<img src="https://g.alicdn.com/sail-web/maas/1.11.39/static/modelscopeIcon.cd89353f.svg" style="width: 120px; height: 20px"/> | 
<img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" style="height:20px">HuggingFace |
Openxlab

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
- Highly cust

## Demo 🎥
demo is coming soon...

## Timeline ⏲️
- [2024.3.14] T2KG Dataset prepared, extracting fine-tuning start
- [2024.3.12] Start the project

## Quick Start 🚀
Firstly, configuration in file `config.py` can be modified according to your needs or local computer environment. The flexible configuration:

| Parameter             | Type | Default Value            |
|-----------------------| --- |--------------------------|
| LLM Model Path        | str | `huggingface repo id`    |
| Chat Function         | bool | `True`                   |
| Knowledge Graph Cache | str | `kg`                     |
| Neo4j Bolt URL        | str | `http://localhost:7474/` |
| Neo4j Username        | str | `neo4j`                  |
| Neo4j Password        | str | `chatkg666`              |

There are two ways to use ChatKG:

- Try the ChatKG on OpenXLab (in the future)


- Run the ChatKG on your local machine


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

The model and knowledge graph data is not included in the repository and running it locally requires a lot of hardware resources, here is the recommended hardware configuration:
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

## Acknowledgement 🙏

**Special thanks to Shanghai Artificial Intelligence Laboratory for its support of this project.**

