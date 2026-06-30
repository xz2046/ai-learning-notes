from abc import ABC,abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from utils.config_handler import rag_conf


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self):
        chat_model = ChatOpenAI(
            model=rag_conf["chat_model_name"],
            api_key=rag_conf["api_key"],
            base_url=rag_conf["base_url"],
            temperature=rag_conf["temperature"],
            streaming=rag_conf["streaming"],
        )
        return chat_model
    
class EmbeddingsFactory(BaseModelFactory):
    def generator(self):
        embedding_model = HuggingFaceEmbeddings(
            model_name=rag_conf["embeddings_model_local_path"],
            model_kwargs=rag_conf["model_kwargs"],
            encode_kwargs=rag_conf["encode_kwargs"],
        )
        return embedding_model
    
chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingsFactory().generator()


