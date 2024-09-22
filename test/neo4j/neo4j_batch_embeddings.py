from langchain_openai import OpenAIEmbeddings
import neo4j
from dotenv import load_dotenv
import os

from openai import OpenAI

load_dotenv()

URI = 'bolt://localhost:7687'
AUTH = ('neo4j', 'password')
DB_NAME = 'discrete-math-graphrag'


def main():
    driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()

    model = OpenAIEmbeddings(
        model=os.getenv("EMBEDDINGS_NAME1"),
        openai_api_base=os.getenv("EMBEDDINGS_API_BASE1"),
        openai_api_key=os.getenv("EMBEDDINGS_API_KEY1")
    )

    client = OpenAI(
        base_url=os.getenv("EMBEDDINGS_API_BASE1"),
        api_key=os.getenv("EMBEDDINGS_API_KEY1"),
    )

    batch_size = 100
    batch_n = 1
    name_with_embeddings = []
    with driver.session(database=DB_NAME) as session:
        # Fetch all nodes
        result = session.run('MATCH (n) RETURN n.name as name')
        for record in result:
            name = record.get('name')
            # Create embedding for name
            if name is not None:
                name_with_embeddings.append({
                    'name': name,
                    'nameEmbeddings': client.embeddings.create(
                        input=name,
                        model=os.getenv("EMBEDDINGS_NAME1"),
                    ).data[0].embedding,
                })

            # Import when a batch of embeddings is ready; flush buffer
            if len(name_with_embeddings) == batch_size:
                import_batch(driver, name_with_embeddings, batch_n)
                name_with_embeddings = []
                batch_n += 1

    print("Finished processing.")


def import_batch(driver, nodes_with_embeddings, batch_n):
    # Add embeddings to Movie nodes
    driver.execute_query(
        f'UNWIND $nodes AS node '
        'MATCH (m:__Entity__ {name: node.name}) '
        'SET m.nameEmbeddings = node.nameEmbeddings',
        nodes=nodes_with_embeddings, database_=DB_NAME
    )
    print(f'Processed batch {batch_n}.')


if __name__ == '__main__':
    main()
