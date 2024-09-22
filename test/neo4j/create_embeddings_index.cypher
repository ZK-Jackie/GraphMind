// 在使用neo4j_batch_embeddings.py为结点创建embeddings后，再为embeddings创建向量索引
CREATE VECTOR INDEX nodeNameVectorIndex
FOR (m:__Entity__)
ON m.nameEmbeddings

CREATE VECTOR INDEX nodeDescVectorIndex
FOR (m:__Entity__)
ON m.description_embedding