import os
from openai import OpenAI

client =  OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你是一个AI助理"},
        {"role": "user", "content": "小红有三只猫"},
        {"role": "assistant", "content": "我知道了，小红有三只猫。"},
        {"role": "user", "content": "小明有两只狗"},
        {"role": "assistant", "content": "我知道了，小明有两只狗。"},
        {"role": "user", "content": "小红和小明一共有多少只宠物？"},
    ],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="",flush=True)