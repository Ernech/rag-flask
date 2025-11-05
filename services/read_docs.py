from services.vector_store import db_global
from typing import List

def get_results(query:str, sources:List[str]):
    results = db_global.similarity_search_with_score(query, k=8, filter={"source": {"$in": sources}})
    THRESHOLD = 0.6
    relevant_results = [(doc, score) for doc, score in results if score < THRESHOLD]
    return relevant_results