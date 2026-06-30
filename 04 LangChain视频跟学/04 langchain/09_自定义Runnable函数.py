from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
import os

strparser = StrOutputParser()
jsonparser = JsonOutputParser()
model = ChatOpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
)

#自定义一个runnable，功能是将输入的名字进行包装，变成一个新的字符串
my_func = RunnableLambda(lambda x: f"这个名字是：{x}")

first_prompt = PromptTemplate.from_template(
    "我邻居姓：{lastname}，刚生了{gender}，请起名，仅告知我名字无需其它内容。"
)

second_prompt = PromptTemplate.from_template(
    "请根据这个名字：{name}，分析这个名字的寓意，并用一句话总结这个名字的寓意。"
)

#也可以直接使用lambda表达式来创建一个函数，功能同上
#chain = first_prompt | model | (lambda ai_msg : {"name": ai_msg.content}) | second_prompt | model | strparser 
chain = first_prompt | model | my_func | second_prompt | model | strparser


res: str = chain.invoke({"lastname": "张", "gender": "女儿"})
print(res)
print(type(res))
