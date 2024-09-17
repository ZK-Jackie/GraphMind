import os
import time
import jinja2
import shutil

from graphrag.index.cli import index_cli
from typing_extensions import Self

from pydantic import model_validator, Field, ConfigDict

from graphmind.adapter.engine import BaseEngine, SUPPORT_CONFIG
from graphmind.adapter.llm import TaskZhipuAI, EmbeddingsZhipuAI
from graphmind.utils.file_reader import find_file


# TODO 从输入输出上看，更加符合一个Builder的机制，后续要修改为Builder类
class GraphragEngine(BaseEngine):
    input_dir: str | list[str] = Field(description="Input file directory")
    """用户文件输入目录"""

    input_type: str | list[str] = Field(description="Input file type", default="txt")
    """用户文件输入类型"""

    entity_types: list[str] = Field(description="Entity types", default=["概念", "定理", "性质", "原理", "算法", "数学家"])
    """实体类型"""

    skip_workflows: str | list[str] = Field(description="Skip workflows", default=[
        "create_base_documents",
        "create_base_text_units",
        "create_final_communities",
        "create_final_community_reports",
        "create_final_covariates",
        "create_final_documents",
        "create_final_text_units",
        "join_text_units_to_covariate_ids",
        "join_text_units_to_entity_ids",
        "join_text_units_to_relationship_ids"
    ])
    """跳过的工作流配置"""

    config_template_path: str | None = Field(description="Custom configuration file path",
                                             default="config/template.yaml")
    """自定义配置文件路径"""

    prompt_path: str | None = Field(description="Default configuration file path", default="prompts")
    """默认提示词文件路径"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """pydantic 配置：允许任意类型"""

    @model_validator(mode="after")  # 由于是after模式，字段已经初始化，此处就可以使用self了
    def validate_environment(self) -> Self:
        # 1 检测是否提供了 llm 和 embeddings
        if not self.llm or not self.embeddings:
            raise ValueError("Please provide the llm and embeddings.")
        # 2 检测是否提供了 work_dir
        self.work_dir = self.work_dir or f"{os.getcwd()}/work_dir/{time.strftime('%Y%m%d%H%M%S')}"
        # 3 检测是否提供了 input_dir
        self.input_dir = self.input_dir or os.getenv("INPUT_DIR")
        if not self.input_dir:
            raise ValueError("Please provide the input directory.")
        # 4 检测文件输入类型是否合法
        if isinstance(self.input_type, str):
            self.input_type = [self.input_type]
        if not all([t in SUPPORT_CONFIG.GRAPHRAG_FILE_SUPPORT for t in self.input_type]):
            raise ValueError(f"Unsupported input type: {self.input_type}")
        return self  # 一定不要忘记返回self！！

    # 运行+插入数据库，结束
    def execute(self, **kwargs):
        # 1 初始化工作目录
        self._execute_input_init()
        # 2 初始化配置模板
        self._execute_config_init()
        # 3 从main入口运行Graphrag
        # self._execute_graphrag_run()
        return self

    def _execute_input_init(self):
        # 1 找用户目录下的文件，复制文件到input目录
        os.makedirs(f"{self.work_dir}/input", exist_ok=True)
        file_list = find_file(self.input_dir, self.input_type)
        if not file_list:
            raise FileNotFoundError(f"No files found in {self.input_dir}")
        for file in file_list:
            shutil.copy(file, f"{self.work_dir}/input")
        # 2 复制配置模板到工作目录
        shutil.copy(self.config_template_path, f"{self.work_dir}/settings.yaml")
        # 3 复制所有提示词到prompts目录
        shutil.copytree(self.prompt_path, f"{self.work_dir}/prompts")

    def _execute_config_init(self):
        # 1 读取配置模板
        with open(f"{self.work_dir}/settings.yaml", "r",  encoding='utf-8') as f:
            template = f.read()
        # 2 渲染配置模板
        # 先准备好正则表达式
        reg_type_content = "|".join(self.input_type)
        # 填充模板
        template = jinja2.Template(template)
        config = template.render(
            skip_workflows=self.skip_workflows,
            llm_model_name=self.llm.llm_name,
            llm_api_key=self.llm.api_key,
            llm_api_base=self.llm.api_base,
            llm_concur_num=5,

            embeddings_model_name=self.embeddings.embeddings_name,
            embeddings_api_key=self.embeddings.api_key,
            embeddings_api_base=self.embeddings.api_base,
            embeddings_concur_num=1,

            input_file_pattern=f'".*\\\\.({reg_type_content})$"',

            entity_types=self.entity_types,
        )
        # 3 写入配置文件
        with open(f"{self.work_dir}/settings.yaml", "w", encoding='utf-8') as f:
            f.write(config)

    def _execute_graphrag_run(self):
        index_cli(
            root_dir=self.work_dir,
            verbose=False,
            resume=None,
            update_index_id=None,
            memprofile=False,
            nocache=False,
            reporter="rich",  # rich, print, none
            config_filepath=None,
            emit="parquet",  # parquet, csv, json
            dryrun=False,
            init=False,
            skip_validations=False,
        )

    def persist_local(self):
        pass

    def persist_database(self):
        pass


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"),
                           api_key=os.getenv("ZHIPU_API_KEY"),
                           api_base=os.getenv("ZHIPU_API_BASE"))
    embedding_llm = EmbeddingsZhipuAI(embeddings_name=os.getenv("EMBEDDINGS_NAME1"),
                                      api_key=os.getenv("EMBEDDINGS_API_KEY1"),
                                      api_base=os.getenv("EMBEDDINGS_API_BASE1"))
    engine = GraphragEngine(llm=task_llm,
                            input_type=["txt", "md"],
                            input_dir="input",
                            prompt_path="prompts/textbook_zh",
                            embeddings=embedding_llm).execute()
