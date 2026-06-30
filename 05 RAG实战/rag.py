
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda
from langchain_openai import ChatOpenAI
import os

from vector_store import VectorStoreService,get_embedding
from file_history_store import get_history
import config_data


class RagServer(object):
    def __init__(self):
        embedding = get_embedding()
        self.vector_server = VectorStoreService(embedding=embedding)
        self.prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "你是一个业务运维助手，以我提供的参考资料为主，"
                    "简洁且专业的回答用户提问。如果参考资料中不包含回答问题所需的信息，请如实告诉用户找不到相关信息。参考资料："
                    "{context}\n"
                    "以下是历史对话记录：\n"
                ),
                MessagesPlaceholder("history"),
                ("user", "请回答用户提问：{input}"),
            ]
        )
        self.chat_model = ChatOpenAI(
            model="deepseek-v4-flash",
            api_key=os.environ.get("DEEPSEEK_API_KEY2"),
            base_url="https://api.deepseek.com",
            temperature=0.3,
            streaming=True,
        )
        self.chain = self.__get_chain()

    def __get_chain(self):
        # 获取最终执行链
        retriever = self.vector_server.get_retriever()

        def format_document(docs: list[Document]):
            if not docs:
                return "无相关参考资料"
            format_str = ""
            for doc in docs:
                format_str += (
                    f"参考片段:{doc.page_content}\n文档元数据:{doc.metadata}\n\n"
                )
            return format_str

        def format_for_retriever(value: dict):
            return value["input"]

        def format_for_prompt(value):
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value

        chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever)
                | retriever
                | format_document,
            }
            | RunnableLambda(format_for_prompt)
            | self.prompt_template
            | self.chat_model
            | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        return conversation_chain


# if __name__ == "__main__":
#     os.chdir(os.path.dirname(__file__))

#     session_config = {"configurable": {"session_id": "user_001"}}
#     res = RagServer().chain.invoke({"input": "PDD的appid有那些？"}, session_config)
#     print(res)
