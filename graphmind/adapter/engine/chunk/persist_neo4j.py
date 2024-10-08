import os
from typing import Any
import shortuuid
import pandas as pd
from neo4j import Driver
import time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GraphragPersist(BaseModel):
    database_type: str = Field(description="Database type", default="neo4j")
    client: Driver = Field(description="Neo4j driver", default=None)
    database_name: str = Field(description="Neo4j database name", default="neo4j")
    book_name: str = Field(description="Book name", default=None)
    folder_path: str = Field(description="Folder path", default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    def validate_connection(cls, values: Any) -> Any:
        values["database_type"] = values.get("database_type") or os.getenv("DATABASE_TYPE") or "neo4j"
        if not values["client"]:
            raise RuntimeError("GraphragPersist Neo4j client cannot be `None`")
        if not values["folder_path"]:
            raise RuntimeError("GraphragPersist folder path cannot be `None`")
        values["database_name"] = values.get("database_name") or os.getenv("DATABASE_NAME") or "neo4j"
        values["book_name"] = values.get("book_name") or os.getenv("BOOK_NAME") or "book"
        return values

    # 工具函数
    def batched_import(self, statement, df, batch_size=1000):
        total = len(df)
        start_s = time.time()
        for start in range(0, total, batch_size):
            batch = df.iloc[start: min(start + batch_size, total)]
            result = self.client.execute_query("UNWIND $rows AS value " + statement,
                                               rows=batch.to_dict('records'),
                                               database_=self.database_name)
            print(result.summary.counters)
        print(f'{total} rows in {time.time() - start_s} s.')
        return total

    def persist(self):
        statement_part = f"""
        CREATE CONSTRAINT unique_node_{shortuuid.ShortUUID().random(5)} IF NOT EXISTS FOR (n:{self.book_name}) REQUIRE (n.id, n.name) IS UNIQUE;
        CREATE CONSTRAINT unique_rel_{shortuuid.ShortUUID().random(5)} IF NOT EXISTS FOR ()-[rel:RELATED]->() REQUIRE (rel.id, rel.book) IS UNIQUE;
        """.split(";")
        for statement in statement_part:
            if len((statement or "").strip()) > 0:
                self.client.execute_query(statement)

        # 导入实体
        entity_df = pd.read_parquet(f'{self.folder_path}/create_final_entities.parquet',
                                    columns=["name", "type", "description", "human_readable_id", "id",
                                             "description_embedding", "text_unit_ids"])
        entity_df.head(2)
        entity_statement = f"""  
            MERGE (e:__Entity__:{self.book_name} {{id:value.id}})  
            SET e += value {{.human_readable_id, .description, name:replace(value.name,'"','')}}  
            WITH e, value  
            CALL db.create.setNodeVectorProperty(e, "description_embedding", value.description_embedding)  
            CALL apoc.create.addLabels(e, case when coalesce(value.type,"") = "" then [] else [apoc.text.upperCamelCase(replace(value.type,'"',''))] end) yield node  
            UNWIND value.text_unit_ids AS text_unit  
            MATCH (c:__Chunk__ {{id:text_unit}})  
            MERGE (c)-[:HAS_ENTITY]->(e)  
        """
        self.batched_import(entity_statement, entity_df)

        # 4.2 导入实体关系
        rel_df = pd.read_parquet(f'{self.folder_path}/create_final_relationships.parquet',
                                 columns=["source", "target", "id", "rank", "weight", "human_readable_id",
                                          "description", "text_unit_ids"])
        rel_df.head(2)
        rel_statement = f"""  
            MATCH (source:__Entity__:{self.book_name} {{name:replace(value.source,'"','')}})  
            MATCH (target:__Entity__:{self.book_name} {{name:replace(value.target,'"','')}})  
            // not necessary to merge on id as there is only one relationship per pair  
            MERGE (source)-[rel:RELATED {{id: value.id, book: "{self.book_name}"}}]->(target)  
            SET rel += value {{.rank, .weight, .human_readable_id, .description, .text_unit_ids}}  
            RETURN count(*) as createdRels  
        """
        self.batched_import(rel_statement, rel_df)
