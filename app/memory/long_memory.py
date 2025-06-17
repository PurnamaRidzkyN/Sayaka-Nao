import time
from flask import jsonify
from sentence_transformers import SentenceTransformer
import chromadb
from app.utils.chunk_helper import chunk_text
import uuid


class longMemory:
    def __init__(self,
                 chroma_path: str = "./memory/memory_db",
                 collection_name: str = "knowledge_memory",
                 model_name: str = "all-MiniLM-L6-v2"):
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection_name = collection_name
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        self.short_memory_file = "app/memory/short_memory"
        self.model = SentenceTransformer(model_name)

    def add_memory(self, summary: str,topic: str):
        if not summary.strip():
            raise ValueError("Summary tidak boleh kosong")

        timestamp = int(time.time())
        chunks = chunk_text(summary)
        
        for i, chunk in enumerate(chunks):
            unique_id = str(uuid.uuid4())
            embedding = self.model.encode(chunk).tolist()

            self.collection.add(
                embeddings=[embedding],
                documents=[chunk],  # ini yang akan dicari berdasarkan kemiripan
                metadatas=[{
                    "timestamp": timestamp,
                    "chunk_index": i,
                    "topic": topic
                }],
                ids=[unique_id],
            )


    def get_memory(self, query: str, top_k: int = 5) -> str:
        query_embedding = self.model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        scored_chunks = []
        for doc, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            scored_chunks.append((distance, doc))

        scored_chunks.sort(key=lambda x: x[0])  # sort berdasarkan jarak terkecil (terdekat)
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


    