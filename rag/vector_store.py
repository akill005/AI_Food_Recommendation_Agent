import json

from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

with open("data/menu.json") as f:
    menu = json.load(f)

docs = []

for item in menu:

    text = f"""
    Food: {item['name']}
    Restaurant: {item['restaurant']}
    Price: {item['price']}
    Type: {item['type']}
    Protein: {item['protein']}
    Rating: {item['rating']}
    """

    docs.append(
        Document(
            page_content=text,
            metadata=item
        )
    )

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = FAISS.from_documents(docs, embeddings)

retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 6}
)