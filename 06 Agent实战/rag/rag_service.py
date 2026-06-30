from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from model.factory import chat_model

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt

class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template  | self.model | StrOutputParser()
        return chain
    
    def retriever_docs(self,query:str) -> list[Document]:
        return self.retriever.invoke(query)
    
    def rag_summarize(self,query:str):
        context_docs = self.retriever_docs(query)
        context = ""
        count = 0
        for doc in context_docs:
            count += 1
            context += f"【参考资料{count}】:参考资料:{doc.page_content} | 资料元数据:{doc.metadata}\n"

        return self.chain.invoke({
            "input":query,
            "context":context
        })
    
if __name__ =="__main__":
    rag = RagSummarizeService()
    res = rag.rag_summarize("工厂函数的作用")
    print(res)