from openai import OpenAI

# 1. 修正协议 + 加占位 api_key，骗过 SDK 校验
client = OpenAI(
    base_url="http://localhost:11434/v1",  # 注意是 http，不是 https
    api_key="ollama"  # 随便填一个字符串即可，Ollama 不校验
)

# 2. 去掉不兼容的参数，仅保留 Ollama 支持的字段
response = client.chat.completions.create(
    model="deepseek-r1:7b",  # 确保 Ollama 里已经下载了这个模型
    messages=[
        {"role": "system", "content": "你是一个乐于助人的编程助手"},
        {"role": "user", "content": "我现在用openai调用你，是否调用成功了？"},
    ],
    stream=False  # 非流式输出
)

# 3. 打印返回结果
print(response.choices[0].message.content)