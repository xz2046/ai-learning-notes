import os
from openai import OpenAI

client =  OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你是一个乐于助人的编程助手"},
        {"role": "assistant", "content": "我是一个乐于助人的编程助手，请问需要完成什么任务吗？"},
        {"role": "user", "content": "帮我完成一个二分查找python函数"},
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="",flush=True)