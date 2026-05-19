from typing import Optional
from pydantic import BaseModel
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.query_parser import extract_filters_rule_based
from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    hit_rate,
    measure_latency
)
from evaluation.logger import log_metrics
from rapidfuzz import fuzz
from rank_bm25 import BM25Okapi
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
from rag.vector_store import (
    vector_db,
    bm25,
    documents
)
class FoodQuery(BaseModel):

    name: Optional[str] = None
    protein: Optional[str] = None
    restaurant: Optional[str] = None
    type: Optional[str] = None
    max_price: Optional[int] = None
    min_price: Optional[int] = None
    intent: Optional[str] = None

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0
)

parser = JsonOutputParser(
    pydantic_object=FoodQuery
)
extract_prompt = ChatPromptTemplate.from_template(
    """
Extract food search filters.
Return ONLY JSON.
User Query:
{query}

{format_instructions}
"""
)
chain = (
    extract_prompt
    | llm
    | parser
)

def needs_llm(filters):
    important_fields = [
        "name",
        "protein",
        "type",
        "max_price",
        "min_price"
    ]
    extracted = sum(
        1 for f in important_fields
        if filters.get(f) is not None
    )
    return extracted < 3

def matches(metadata_value, filter_value, field=None):

    if not metadata_value or not filter_value:
        return False
    metadata_value = str(metadata_value).strip().lower()
    filter_value = str(filter_value).strip().lower()
    strict_fields = [
        "protein",
        "type"
    ]

    if field in strict_fields:
        return metadata_value == filter_value

    if filter_value in metadata_value:
        return True
    
    score = fuzz.partial_ratio(
        metadata_value,
        filter_value
    )
    return score >= 80

def reciprocal_rank_fusion(
    dense_docs,
    sparse_docs,
    k=60
):

    scores = {}
    # Dense scores
    for rank, doc in enumerate(dense_docs):
        doc_id = doc.page_content
        scores[doc_id] = scores.get(doc_id, 0) + (
            1 / (k + rank + 1)
        )
    # Sparse scores
    for rank, doc in enumerate(sparse_docs):
        doc_id = doc.page_content
        scores[doc_id] = scores.get(doc_id, 0) + (
            1 / (k + rank + 1)
        )
    reranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    final_docs = []
    for doc_id, _ in reranked:
        for d in dense_docs + sparse_docs:
            if d.page_content == doc_id:
                final_docs.append(d)
                break
    return final_docs

@tool
def search_food(query: str) -> str:
    """
    Hybrid Search Food Recommendation Tool
    """
    try:

        logger.info(f"Query: {query}")
        filters = extract_filters_rule_based(
            query
        )
        if needs_llm(filters):
            logger.info(
                "Using LLM extraction fallback"
            )
            llm_filters = chain.invoke(
                {
                    "query": query,
                    "format_instructions":
                    parser.get_format_instructions()
                }
            )

            llm_filters = dict(llm_filters)
            for key, value in llm_filters.items():
                if filters.get(key) is None:
                    filters[key] = value
        if filters.get("name") is None and filters.get("protein") is None:
            logger.info("No strong filters detected → fallback to query")
            filters["name"] = query
        else:

            logger.info(
                "Rule-based extraction sufficient"
            )
        logger.info(f"Filters: {filters}")
        dense_docs, latency = measure_latency(
            vector_db.similarity_search,
            query,
            k=25
        )

        logger.info(f"Retrieval latency: {latency}s")
        tokenized_query = query.lower().split()
        bm25_scores = bm25.get_scores(
            tokenized_query
        )
        top_indices = sorted(
            range(len(bm25_scores)),
            key=lambda i: bm25_scores[i],
            reverse=True
        )[:10]

        top_indices = [
            i for i in top_indices
            if bm25_scores[i] > 0
        ]
        sparse_docs = [
            documents[i]
            for i in top_indices
        ]
        retrieved_docs = reciprocal_rank_fusion(
            dense_docs,
            sparse_docs
        )
        filtered_docs = []
        for doc in retrieved_docs:
            metadata = doc.metadata
            matched = True
            for key, value in filters.items():
                if value is None:
                    continue
                # Max price
                if key == "max_price":
                    if float(metadata.get("price", 0)) > value:
                        matched = False
                        break
                # Min price
                elif key == "min_price":
                    if float(metadata.get("price", 0)) < value:
                        matched = False
                        break
                else:
                    if not matches(
                        metadata.get(key, ""),
                        value,
                        field=key
                    ):
                        matched = False
                        break
            if matched:
                filtered_docs.append(doc)

        if not filtered_docs:
            requested_food = filters.get("name")
            requested_protein = filters.get("protein")
            matching_items = []
            for doc in retrieved_docs:
                item_name = str(
                    doc.metadata.get("name", "")
                ).lower()
                item_protein = str(
                    doc.metadata.get("protein", "")
                ).lower()
                food_match = (
                    requested_food
                    and requested_food.lower() in item_name
                )
                protein_match = (
                    not requested_protein
                    or requested_protein.lower() == item_protein
                )
                if food_match and protein_match:
                    matching_items.append(doc)
            if matching_items:
                if filters.get("max_price") is not None:
                    cheapest_item = min(
                        matching_items,
                        key=lambda x: float(
                            x.metadata.get("price", 0)
                        )
                    )
                    cheapest_price = cheapest_item.metadata.get("price")
                    food_name = cheapest_item.metadata.get("name")
                    return (
                        f"{food_name} is currently unavailable "
                        f"under ₹{filters.get('max_price')}. "
                        f"The lowest available price is ₹{cheapest_price}."
                    )
                matching_items = sorted(
                    matching_items,
                    key=lambda x: (
                        float(x.metadata.get("rating", 0)),
                        -float(x.metadata.get("price", 0))
                    ),
                    reverse=True
                )
                results = []
                TOP_K = 3
                for i, d in enumerate(matching_items[:TOP_K], 1):
                    m = d.metadata
                    results.append(
                        f"""
            Food: {m.get('name')}
            Restaurant: {m.get('restaurant')}
            Price: ₹{m.get('price')}
            Type: {m.get('type')}
            Protein: {m.get('protein')}
            Rating: {m.get('rating')} ⭐
            """
                    )
                return "\n".join(results)
            return (
                "Currently we do not have this item available."
            )

        def ranking_score(doc):
            rating = float(
                doc.metadata.get("rating", 0)
            )
            price = float(
                doc.metadata.get("price", 1)
            )
            affordability_score = 1 / price
            final_score = (
                (0.8 * rating)
                +
                (0.2 * affordability_score * 100)
            )
            return final_score

        filtered_docs = sorted(
            filtered_docs,
            key=ranking_score,
            reverse=True
        )
        results = []
        for i, d in enumerate(filtered_docs[:3], 1):
            m = d.metadata
            results.append(
                f"""
Food: {m.get('name')}
Restaurant: {m.get('restaurant')}
Price: ₹{m.get('price')}
Type: {m.get('type')}
Protein: {m.get('protein')}
Rating: {m.get('rating')} ⭐
"""
            )
        recommended_items = [
            (
                d.metadata.get("name", "").lower(),
                d.metadata.get("restaurant", "").lower()
            )
            for d in filtered_docs[:5]
        ]
        relevant_items = (
    [
        (
            filters.get("name", "").lower(),
            d.metadata.get("restaurant", "").lower()
        )
        for d in filtered_docs[:5]
    ]
    if filters.get("name")
    else []
)
        precision = precision_at_k(
            recommended_items,
            relevant_items,
            k=5
        )
        recall = recall_at_k(
            recommended_items,
            relevant_items,
            k=5
        )
        hit = hit_rate(
            recommended_items,
            relevant_items,
            k=5
        )
        logger.info(f"Precision@5: {precision}")
        logger.info(f"Recall@5: {recall}")
        logger.info(f"Hit Rate@5: {hit}")
        log_metrics(
            query=query,
            precision=precision,
            recall=recall,
            hit_rate=hit,
            latency=latency,
            results_count=len(filtered_docs[:5])
        )
        return "\n".join(results)
    except Exception as e:
        logger.error(str(e), exc_info=True)
        return f"Error: {str(e)}"