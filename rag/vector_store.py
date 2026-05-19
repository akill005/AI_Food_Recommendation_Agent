import json
import requests
import logging
from rank_bm25 import BM25Okapi
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

logger = logging.getLogger(__name__)
_vector_db_cache = None
_embeddings_cache = None
bm25 = None
documents = []
tokenized_docs = []

def _fetch_menu_data():
    try:
        API_URL = "http://localhost:5000/menu"
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API fetch failed: {str(e)}")
        with open("data/menu.json") as f:
            return json.load(f)

def _create_documents(menu):
    docs = []
    for item in menu:
        text = f"""
        Food: {item.get('name')}
        Restaurant: {item.get('restaurant')}
        Price: {item.get('price')}
        Type: {item.get('type')}
        Protein: {item.get('protein')}
        Rating: {item.get('rating')}
        """
        docs.append(
            Document(
                page_content=text,
                metadata=item
            )
        )
    return docs

def get_embeddings():
    global _embeddings_cache
    if _embeddings_cache is None:
        _embeddings_cache = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings_cache

def get_vector_db():
    global _vector_db_cache
    global bm25
    global documents
    global tokenized_docs
    if _vector_db_cache is not None:
        return _vector_db_cache
    logger.info("Initializing Hybrid Retrieval System...")
    menu = _fetch_menu_data()
    docs = _create_documents(menu)
    documents = docs
    embeddings = get_embeddings()
    _vector_db_cache = FAISS.from_documents(
        docs,
        embeddings
    )
    logger.info("FAISS initialized")
    tokenized_docs = [
        doc.page_content.lower().split()
        for doc in docs
    ]
    bm25 = BM25Okapi(tokenized_docs)
    logger.info("BM25 initialized")
    return _vector_db_cache
vector_db = get_vector_db()
embeddings = get_embeddings()