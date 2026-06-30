from openai import OpenAI
import os

client = OpenAI( api_key=os.environ.get('DEEPSEEK_API_KEY2'), 
                base_url="https://api.deepseek.com")

messages = [{"role": "user", "content": "9.11和9.8那个大"}]
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    stream=True,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)

print("模型思考过程：")
reasoning_content = ""
content = ""

# 实时流式打印
for chunk in response:
    delta = chunk.choices[0].delta
    if delta.reasoning_content:
        # 实时打印思考片段
        print(delta.reasoning_content, end="", flush=True)
        reasoning_content += delta.reasoning_content
    elif delta.content:
        # 实时打印回答片段
        print(delta.content, end="", flush=True)
        content += delta.content

print("\n\n完整思考：", reasoning_content)
print("完整回答：", content)