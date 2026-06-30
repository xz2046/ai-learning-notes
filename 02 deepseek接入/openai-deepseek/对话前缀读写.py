import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com/beta")

#设置 assistant 开头的消息为 "```python\n" 来强制模型输出 python 代码，并设置 stop 参数为 ['```'] 来避免模型的额外解释。
messages = [
    {"role": "user", "content": "帮我写一个二分查找的python代码"},
    {"role": "assistant", "content": "```python\n", "prefix": True}
]
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    stop=["```"],
)
print(response.choices[0].message.content)
