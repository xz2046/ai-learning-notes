from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
import os

model = ChatOpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
)
strparser = StrOutputParser()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个历史记录助手，需要根据用户会话历史回答用户问题，并记录用户需求。",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)


store = {}


def print_prompt(full_prompt):
    print("=" * 20, full_prompt.to_string(), "=" * 20,end="\n\n")
    return full_prompt


def get_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


base_chain = prompt | print_prompt | model | strparser

chain_with_history = RunnableWithMessageHistory(
    base_chain,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)


if __name__ == "__main__":
    session_config = {"configurable": {"session_id": "user_001"}}

    res1 = chain_with_history.invoke(
        {"input": "今天早上有雾，中午天气是晴天"}, config=session_config
    )
    print("第一次结果：", res1)
    res2 = chain_with_history.invoke({"input": "今天晚上有雨"}, config=session_config)
    print("第二次结果：", res2)
    res3 = chain_with_history.invoke(
        {"input": "今天整体天气情况如何。"}, config=session_config
    )
    print("第三次结果：", res3)
