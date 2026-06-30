from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="./05 插入部分-视频跟学/098 testData/test.json",
    jq_schema=".milestones.[].year",
    text_content=False,  # 告知JSONLoader 我抽取的内容不是字符串
    json_lines=True,  # 告知JSONLoader 这是一个JSONLines文件（每一行都是一个独立的标准JSON）
)

data = loader.load()

print(data)
