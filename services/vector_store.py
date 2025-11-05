# services/vector_store.py
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BBDD_VECTORIAL_PATH = os.getenv("BBDD_VECTORIAL_PATH")
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH")
os.makedirs(BBDD_VECTORIAL_PATH, exist_ok=True)
embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_PATH)

# ✅ Esta instancia se crea una sola vez, cuando Flask arranca
db_global = Chroma(
    persist_directory=BBDD_VECTORIAL_PATH,
    embedding_function=embedding_function
)
