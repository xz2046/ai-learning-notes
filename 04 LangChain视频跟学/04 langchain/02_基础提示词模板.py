from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com",
    temperature=0.7,
)


prompt = PromptTemplate.from_template("你是一个{role}助手，请用{style}的风格回答问题。")
# formatted_prompt = prompt.format(role="专业", style="夸张")
# response = llm(formatted_prompt + "什么是RAG？")

chain = prompt | llm
response = chain.invoke({"role": "专业", "style": "夸张"})
print(response)