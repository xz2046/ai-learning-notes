from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os

strparser = StrOutputParser()
jsonparser = JsonOutputParser()
model = ChatOpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
)
first_prompt = PromptTemplate.from_template(
    "我邻居姓：{lastname}，刚生了{gender}，请起名，仅告知我名字无需其它内容。"
    "请严格以json格式返回，包含一个字段name，值为名字。"
)

second_prompt = PromptTemplate.from_template(
    "请根据这个名字：{name}，分析这个名字的寓意，并用一句话总结这个名字的寓意。"
)
chain = first_prompt | model | jsonparser | second_prompt | model | strparser

for chunk in chain.stream({"lastname": "张", "gender": "女儿"}):
    print(chunk,end="",flush=True)
