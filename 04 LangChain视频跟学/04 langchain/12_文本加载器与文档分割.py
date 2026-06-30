from langchain_community.document_loaders import TextLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

loader = TextLoader(
    file_path="C:/Users/admin/Desktop/学习/05 插入部分-视频跟学/098 testData/text.txt",
    encoding="utf-8",
)

docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=10,  # 分段最大字符数
    chunk_overlap=5,  # 分段重叠字符数
    separators=[
        "\n\n",
        "\n",
        " ",
        "",
    ],  # 分段优先级，遇到优先级高的分段符就分段，遇不到就继续往下找
    length_function=len,  # 计算文本长度的函数，默认为len，也可以自定义，比如计算字数而不是字符数)
)

splitted_docs = splitter.split_documents(docs)
print(len(splitted_docs), splitted_docs)
