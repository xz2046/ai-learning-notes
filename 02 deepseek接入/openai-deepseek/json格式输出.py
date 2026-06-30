import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com",
)

system_prompt = """
用户将提供一些考试文本。请解析 “问题” 和 “答案”，并以 JSON 格式输出。 
示例输入： 世界上最高的山是哪座？
示例 JSON 输出：
{
    "问题": "世界上最高的山是哪座？",
    "答案": "珠穆朗玛峰"
}
"""

user_prompt = "世界上最大的动物是什么，有多大？"

messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    # 通过 response_format 参数指定输出格式为 JSON 对象
    response_format={
        'type': 'json_object'
    } 
)

print(json.loads(response.choices[0].message.content))