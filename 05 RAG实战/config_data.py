md5_path = "./conf/md5_text.txt"

#chroma
collection_name = "RAG_Test"
collection_path = "./data/chroma/"

#locla embeddings model
embeddings_model_name = "BAAI/bge-m3"
local_embeddings_model_path = r"C:/Users/admin/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181"

#spliter
chunk_size = 800
chunk_overlap = 100
separators =[
                "\n\n",
                "\n",
                "。",
                "?",
                "！",
                " ",
                "",
            ]
max_split_char_number = 800

top_k = 3
max_distance = 0.8

storage_path =  "./data/chat_history"

session_config = {"configurable": {"session_id": "user_001"}}
