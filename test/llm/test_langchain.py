from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()


model = OpenAIEmbeddings(
    model="embedding-3",
    openai_api_base=os.getenv("EMBEDDINGS_API_BASE"),
    openai_api_key=os.getenv("EMBEDDINGS_API_KEY")
)

vector_list = model.embed_documents(["first phrase", "second phrase", "third phrase"])

for i, vector in enumerate(vector_list):
    print(f"document {i}: {vector}")

