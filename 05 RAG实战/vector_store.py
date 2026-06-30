from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import RunnableLambda
import config_data


class VectorStoreService(object):
    def __init__(self, embedding):
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=config_data.collection_name,
            persist_directory=config_data.collection_path,
            embedding_function=self.embedding,
        )

    def get_retriever(self):
        """返回自定义检索器：搜索 → 按距离阈值过滤 → 返回文档列表。"""

        def _search(query: str):
            docs_with_scores = (
                self.vector_store.similarity_search_with_relevance_scores(
                    query, k=config_data.top_k
                )
            )
            filtered = [
                doc
                for doc, score in docs_with_scores
                if score < config_data.max_distance
            ]
            return filtered

        return RunnableLambda(_search)


_embedding_instance = None


def get_embedding():
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = HuggingFaceEmbeddings(
            model_name=config_data.local_embeddings_model_path,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_instance
