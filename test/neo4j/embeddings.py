from sentence_transformers import SentenceTransformer
import neo4j


URI = '<URI for Neo4j database>'
AUTH = ('<Username>', '<Password>')
DB_NAME = '<Database name>'  # examples: 'recommendations-50', 'neo4j'


def main():
    driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()

    model = SentenceTransformer('all-MiniLM-L6-v2')  # vector size 384

    batch_size = 100
    batch_n = 1
    movies_with_embeddings = []
    with driver.session(database=DB_NAME) as session:
        # Fetch `Movie` nodes
        result = session.run('MATCH (m:Movie) RETURN m.plot AS plot, m.title AS title')
        for record in result:
            title = record.get('title')
            plot = record.get('plot')

            # Create embedding for title and plot
            if title is not None and plot is not None:
                movies_with_embeddings.append({
                    'title': title,
                    'plot': plot,
                    'embedding': model.encode(f'''
                        Title: {title}\n
                        Plot: {plot}
                    '''),
                })

            # Import when a batch of movies has embeddings ready; flush buffer
            if len(movies_with_embeddings) == batch_size:
                import_batch(driver, movies_with_embeddings, batch_n)
                movies_with_embeddings = []
                batch_n += 1

    # Import complete, show counters
    records, _, _ = driver.execute_query('''
    MATCH (m:Movie WHERE m.embedding IS NOT NULL)
    RETURN count(*) AS countMoviesWithEmbeddings, size(m.embedding) AS embeddingSize
    ''', database_=DB_NAME)
    print(f"""
Embeddings generated and attached to nodes.
Movie nodes with embeddings: {records[0].get('countMoviesWithEmbeddings')}.
Embedding size: {records[0].get('embeddingSize')}.
    """)


def import_batch(driver, nodes_with_embeddings, batch_n):
    # Add embeddings to Movie nodes
    driver.execute_query('''
    UNWIND $movies as movie
    MATCH (m:Movie {title: movie.title, plot: movie.plot})
    CALL db.create.setNodeVectorProperty(m, 'embedding', movie.embedding)
    ''', movies=nodes_with_embeddings, database_=DB_NAME)
    print(f'Processed batch {batch_n}.')


if __name__ == '__main__':
    main()

'''
Movie nodes with embeddings: 9083.
Embedding size: 384.
'''