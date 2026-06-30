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
        {"role": "user", "content": "我现在用openai调用你，是否调用成功了？"},
    ],
)

print(response.choices[0].message.content)