import graphrag.config.defaults as graphrag_defs
from graphrag.config import GraphRagConfig, LLMParameters, TextEmbeddingConfig, InputConfig, EntityExtractionConfig
from graphrag.config.config_file_loader import load_config_from_file
from win32verstamp import file_type

from graphmind.adapter.llm.base import BaseTaskLLM, BaseTextEmbeddings


class CustomGraphRagConfig:
    graphrag_config: GraphRagConfig | None = None


    def __init__(self,
                 base_config_dir: str,
                 root_dir: str,
                 llm: BaseTaskLLM,
                 embeddings: BaseTextEmbeddings,
                 input_dir: str,
                 base_work_dir: str,
                 prompt_path: str,
                 file_type: str | list[str]):
        if base_config_dir:
            self.graphrag_config = load_config_from_file(base_config_dir)
        self.set_root_dir(root_dir)
        self.set_llm(llm)
        self.set_embeddings(embeddings)
        self.set_input(input_dir)
        self.set_workdir(base_work_dir)
        self.set_entity_extraction(prompt_path)    # 暂时不想支持修改实体类别
        self.set_skip_workflow()        # 暂时不想被支持修改workflow
        self.set_file_type(file_type)

    def set_root_dir(self, root_dir: str):
        self.graphrag_config.root_dir = root_dir
        return self


    def set_llm(self, llm: BaseTaskLLM):
        graphrag_llm_config = LLMParameters()
        graphrag_llm_config.api_key = llm.api_key
        graphrag_llm_config.api_base = llm.api_base
        graphrag_llm_config.model = llm.llm_name
        graphrag_llm_config.model_supports_json = True
        graphrag_llm_config.concurrent_requests = 5
        self.graphrag_config.llm = graphrag_llm_config
        return self

    def set_embeddings(self, embeddings: BaseTextEmbeddings):
        graphrag_embeddings_config = TextEmbeddingConfig()
        graphrag_embeddings_config.llm.api_key = embeddings.api_key
        graphrag_embeddings_config.llm.api_base = embeddings.api_base
        graphrag_embeddings_config.llm.model = embeddings.embeddings_name
        graphrag_embeddings_config.llm.concurrent_requests = 1
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

    def set_entity_extraction(self, prompt_path: str, entity_types: list[str]=None):
        # TODO 检查文件是否存在  检查文件内元素是否都存在
        graphrag_entity_extraction_config = EntityExtractionConfig()
        graphrag_entity_extraction_config.prompt = prompt_path
        # with open("prompt/entity_extraction_en_zh.txt", "r", encoding="utf-8") as f:
        #     graphrag_entity_extraction_config.prompt = f.read()
        graphrag_entity_extraction_config.entity_types = ["概念", "定理", "性质", "原理", "算法", "数学家"]
        graphrag_entity_extraction_config.max_gleanings = 1
        self.graphrag_config.entity_extraction = graphrag_entity_extraction_config
        return self

    def set_file_type(self, file_types: str | list[str]):
        # 输入预处理：去掉所有标点符号，转换为小写，去除首尾空格
        if isinstance(file_types, str):
            file_types = [file_types]
        for i, _ in enumerate(file_types):
            file_types[i] = file_types[i].lower()
            file_types[i] = file_types[i].strip(".")
            file_types[i] = file_types[i].strip()
        reg = f".*\\.({'|'.join(file_types)})$"
        self.graphrag_config.input.file_pattern = reg
        return self

    def get_graphrag_config(self):
        return self.graphrag_config
