import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

file_path = r"C:/Users/admin/Desktop/学习/01 学习计划与基础概念/AI应用开发学习计划.pdf"
loader = PyMuPDFLoader(file_path, 
                       mode="single"#page按页分割，single，整体不分割
                       #password="2222" #指定pdf文档密码
                       )
docs = loader.load()

# 文本分割
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600, chunk_overlap=80, separators=["\n\n", "\n", "。", "！", "？", "，"]
)
split_docs = splitter.split_documents(docs)
print(f"原始页数：{len(docs)}，分割文本块：{len(split_docs)}")
