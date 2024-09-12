import graphrag.config.defaults as graphrag_defs
from graphrag.config import GraphRagConfig, LLMParameters, TextEmbeddingConfig, InputConfig, EntityExtractionConfig
from graphrag.config.config_file_loader import load_config_from_file

from graphmind.adapter.llm.base import BaseTaskLLM, BaseTextEmbeddings


class CustomGraphRagConfig:
    graphrag_config: GraphRagConfig | None = None


    def __init__(self,
                 base_config_dir: str,
                 root_dir: str,
                 llm: BaseTaskLLM,
                 embeddings: BaseTextEmbeddings,
                 input_dir: str,
                 base_work_dir: str):
        if base_config_dir:
            self.graphrag_config = load_config_from_file(base_config_dir)
        self.set_root_dir(root_dir)
        self.set_llm(llm)
        self.set_embeddings(embeddings)
        self.set_input(input_dir)
        self.set_workdir(base_work_dir)
        self.set_entity_extraction()
        self.set_skip_workflow()

    def set_root_dir(self, root_dir: str):
        self.graphrag_config.root_dir = root_dir
        return self


    def set_llm(self, llm: BaseTaskLLM):
        graphrag_llm_config = LLMParameters()
        graphrag_llm_config.api_key = llm.api_key
        graphrag_llm_config.api_base = llm.api_base
        graphrag_llm_config.model = llm.llm_name
        graphrag_llm_config.concurrent_requests = 5
        self.graphrag_config.llm = graphrag_llm_config
        return self

    def set_embeddings(self, embeddings: BaseTextEmbeddings):
        graphrag_embeddings_config = TextEmbeddingConfig()
        graphrag_embeddings_config.api_key = embeddings.api_key
        graphrag_embeddings_config.api_base = embeddings.api_base
        graphrag_embeddings_config.model = embeddings.embeddings_name
        graphrag_embeddings_config.concurrent_requests = 1
        self.graphrag_config.embeddings = graphrag_embeddings_config
        return self

    def set_skip_workflow(self, skip_workflows: list=None):
        if not skip_workflows:
            skip_workflows = ["create_base_documents",
                             "create_base_text_units",
                             "create_final_communities",
                             "create_final_community_reports",
                             "create_final_covariates",
                             "create_final_documents",
                             "create_final_text_units",
                             "join_text_units_to_covariate_ids",
                             "join_text_units_to_entity_ids",
                             "join_text_units_to_relationship_ids"]
        self.graphrag_config.skip_workflows = skip_workflows
        return self

    def set_input(self, input_dir: str):
        graphrag_input_config = InputConfig()
        graphrag_input_config.base_dir = input_dir
        self.graphrag_config.input = graphrag_input_config
        return self

    def set_workdir(self, base_work_dir: str):
        # 1 缓存
        self.graphrag_config.cache.base_dir = f"{base_work_dir}/{graphrag_defs.STORAGE_BASE_DIR}"
        # 2 存储
        self.graphrag_config.storage.base_dir = f"{base_work_dir}/{graphrag_defs.STORAGE_BASE_DIR}"
        # 3 报告
        self.graphrag_config.reporting.base_dir = f"{base_work_dir}/{graphrag_defs.REPORTING_BASE_DIR}"
        return self

    def set_entity_extraction(self, prompt: str=None, entity_types: list[str]=None):
        graphrag_entity_extraction_config = EntityExtractionConfig()
        graphrag_entity_extraction_config.prompt = "prompt/entity_extraction_en_zh.txt"
        # with open("prompt/entity_extraction_en_zh.txt", "r", encoding="utf-8") as f:
        #     graphrag_entity_extraction_config.prompt = f.read()
        graphrag_entity_extraction_config.entity_types = ["概念","算法","方法","定理","性质",
                                                          "术语","作用","数据结构","知识名词"]
        graphrag_entity_extraction_config.max_gleanings = 1
        self.graphrag_config.entity_extraction = graphrag_entity_extraction_config
        return self

    def get_graphrag_config(self):
        return self.graphrag_config
