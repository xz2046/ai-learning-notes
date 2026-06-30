"""
知识库
"""

import os
import hashlib
from datetime import datetime
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config_data
from vector_store import get_embedding


def check_md5(md5_str):
    # 检查传入字符串MD5是否被上传过
    if not os.path.exists(config_data.md5_path):
        open(config_data.md5_path, "w", encoding="utf-8").close()
        return False
    else:
        for line in open(config_data.md5_path, "r", encoding="utf-8").readlines():
            line = line.strip()
            if line == md5_str:
                return True
        return False


def save_md5(md5_str):
    # 将传入的MD5字符串记录到文件保存
    with open(config_data.md5_path, "a", encoding="utf-8") as f:
        f.write(md5_str + "\n")


def get_string_md5(input_str: str, encoding="utf-8"):
    # 将传入字符串转为md5字符串
    str_bytes = input_str.encode(encoding=encoding)
    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    md5_hex = md5_obj.hexdigest()

    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self):
        os.makedirs(config_data.collection_path, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config_data.collection_name,
            embedding_function=get_embedding(),
            persist_directory=config_data.collection_path,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config_data.chunk_size,
            chunk_overlap=config_data.chunk_overlap,
            separators=config_data.separators,
            length_function=len,
        )

    def upload_by_str(self, data, filename):
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过],文档已存在！"

        knowledge_chunks = self.splitter.split_text(data)

        metadata = {
            "filename": filename,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "小杨"
        }

        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex)

        return f"[成功]文件已录入向量库，共切分 {len(knowledge_chunks)} 段"




    def get_file_list(self):
        """从 Chroma 读取所有文档的 metadata，按文件名去重后返回列表。"""
        raw = self.chroma.get(include=["metadatas"])
        seen = set()
        files = []
        for meta in raw.get("metadatas", []):
            name = meta.get("filename", "未知")
            if name not in seen:
                seen.add(name)
                files.append({
                    "filename": name,
                    "datetime": meta.get("datetime", "-"),
                    "operator": meta.get("operator", "-"),
                    "chunks": sum(1 for m in raw["metadatas"] if m.get("filename") == name),
                })
        return files
