import time
import json
from typing import List
from flask import jsonify
from sentence_transformers import SentenceTransformer
import chromadb
import os


class MemoryManager:
    def __init__(self,
                 chroma_path: str = "./memory_db",
                 collection_name: str = "chat_memory",
                 model_name: str = "all-MiniLM-L6-v2",
                 max_chunk_size: int = 500):
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection_name = collection_name
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        self.short_memory_file = "app/memory/short_memory"
        self.model = SentenceTransformer(model_name)
        self.max_chunk_size = max_chunk_size
        self.base_dir = "app/memory/file"

        

    from typing import List

    def chunk_text(self, text: str) -> List[str]:
        chunks = []
        buffer = ""
        
        i = 0
        while i < len(text):
            buffer += text[i]
            i += 1

            # Kalau sudah lewat batas dan ada titik → potong
            if len(buffer) >= self.max_chunk_size:
                # Cek kalau ada titik di buffer
                if '.' in buffer:
                    last_dot = buffer.rfind('.') + 1  # Ambil sampai setelah titik
                    chunks.append(buffer[:last_dot].strip())
                    # Sisakan sisanya ke buffer baru
                    buffer = buffer[last_dot:]

        # Masukkan sisa akhir kalau ada titik
        if buffer.strip():
            chunks.append(buffer.strip())
        
        return chunks


    def add_memory(self, summary: str):
        # Simpan summary ke file
        timestamp = int(time.time())
        filename = f"summary_{timestamp}.txt"
        path = os.path.join(self.base_dir, filename)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(summary)

        # Buat embedding dari summary
        embedding = self.model.encode(summary).tolist()

        # Dapatkan id unik (misal dari jumlah data di collection)
        current_ids = self.collection.get()["ids"]
        new_id = str(len(current_ids))

        # Simpan ke collection dengan metadata path file
        self.collection.add(
            embeddings=[embedding],
            metadatas=[{
                "timestamp": timestamp,
                "path": path
            }],
            ids=[new_id],
        )
        
    def get_memory(self, query: str, top_k: int = 5) -> str:
        query_embedding = self.model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "distances"]
        )

        scored_chunks = []
        for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
            path = metadata.get('path')
            if not path:
                continue

            with open(path, 'r', encoding='utf-8') as f:
                doc = f.read()

            chunks = self.chunk_text(doc)
            for chunk in chunks:
                scored_chunks.append((distance, chunk))

        scored_chunks.sort(key=lambda x: x[0])
        top_chunks = [chunk for _, chunk in scored_chunks[:top_k]]

        memory_text = ""
        for i, chunk in enumerate(top_chunks, 1):
            memory_text += f"[Memory {i}]\n{chunk}\n\n"

        return memory_text.strip()

    def clear_memory(self):
        try:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
            return jsonify({"message": "Semua memori berhasil dihapus."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    def add_to_short_memory(self,filename:str, input_text: str, bot_reply: str):
        # Buat nama file berdasarkan tanggal 
        filepath = os.path.join(self.short_memory_file, filename)  

        # Pastikan folder ada
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Coba baca file jika sudah ada, kalau tidak buat baru
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            memory = []

        entry = {
            "tsuki": input_text,
            "sayaka": bot_reply,
        }

        memory.append(entry)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)

    def get_recent_memory(self, filename, limit=3) -> List[dict]:
        # Buat nama file berdasarkan tanggal 
        filepath = os.path.join(self.short_memory_file, filename)  

        # Pastikan folder ada
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                memory = json.load(f)
                return memory[-limit:]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
