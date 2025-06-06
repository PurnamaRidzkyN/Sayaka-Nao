from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.memory_model import MemoryManager

class KnowledgeSummaryController:
    def __init__(self, chunk_size=1000):
        """
        llm_model: objek model yang punya method invoke(prompt) -> hasil ringkasan
        chunk_size: jumlah karakter maksimal per chunk (bisa juga diubah ke token)
        """
        self.llm_model = ChatGoogleGenerativeAI(model="gemma-3-27b-it", max_tokens=None)
        self.chunk_size = chunk_size
    
    def chunk_text(self, text):
        """
        Memecah text menjadi chunk berdasarkan chunk_size karakter
        """
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i+self.chunk_size])
        return chunks
    
    def summarize_chunk(self, chunk, topic):
        """
        Buat prompt dan panggil model untuk merangkum satu chunk
        """
        prompt = f"""
        Berikut adalah bagian dari transkrip diskusi tentang {topic}:

        {chunk}

        Buatlah rangkuman yang berisi poin-poin penting, konsep utama, dan insight ilmiah dari bagian ini.
        Hasilnya berupa teks narasi yang jelas dan runtut, tanpa kutipan dialog.
        Dokumen ini akan menjadi referensi belajar, jadi jelaskan dengan bahasa yang mudah dimengerti dan terstruktur.
        """
        return self.llm_model.invoke(prompt).strip()
    
    def summarize(self, full_text, topic):
        """
        Proses utama: chunking -> summarize tiap chunk -> gabung ringkasan -> summarize gabungan
        """
        chunks = self.chunk_text(full_text)
        print(f"[INFO] Memecah teks menjadi {len(chunks)} chunk.")
        
        chunk_summaries = []
        for idx, chunk in enumerate(chunks, 1):
            print(f"[INFO] Merangkum chunk {idx}/{len(chunks)}...")
            summary = self.summarize_chunk(chunk, topic)
            chunk_summaries.append(summary)
        
        combined_summary_text = "\n\n".join(chunk_summaries)
        
        # Ringkas semua ringkasan chunk jadi satu ringkasan final
        final_prompt = f"""
        Berikut adalah rangkuman parsial dari diskusi tentang {topic}:

        {combined_summary_text}

        Buatlah rangkuman akhir yang menggabungkan semua poin penting dan insight, dengan bahasa yang mudah dipahami dan runtut.
        """
        print("[INFO] Membuat ringkasan akhir dari semua ringkasan chunk...")
        final_summary = self.llm_model.invoke(final_prompt).strip()
        return final_summary
    
    def revise_summary(self, current_summary, user_feedback, topic):
        prompt = f"""
        Berikut adalah ringkasan diskusi tentang {topic}:

        {current_summary}

        User memberikan masukan/revisi berikut: {user_feedback}

        Perbaiki dan perbaharui ringkasan di atas berdasarkan masukan tersebut.
        Buat hasil yang tetap jelas, runtut, dan mudah dipahami.
        """
        final_summary = self.llm_model.invoke(prompt).strip()
        return final_summary
    
    def process_revision(self,current_summary: str, user_feedback: str, topic: str,):
        """
        Memproses revisi ringkasan berdasarkan masukan user.
        
        Args:
            current_summary (str): Ringkasan saat ini yang akan direvisi.
            user_feedback (str): Masukan/revisi dari user.
            topic (str): Topik diskusi.
            controller: Objek yang memiliki method revise_summary(current_summary, user_feedback, topic).
        
        Returns:
            dict: {'status': 'success', 'revised_summary': hasil_revisi} atau
                {'status': 'error', 'message': error_message}
        """
        try:
            revised = self.revise_summary(current_summary, user_feedback, topic)
            return {
                "status": "success",
                "revised_summary": revised
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Gagal merevisi ringkasan: {str(e)}"
            }

    def create_new_memories(self, final_summary):
        """
        Simpan ringkasan final sebagai memori baru,
        return dict hasil untuk response JSON di web.
        """
        try:
            MemoryManager().add_memory(final_summary, important=True)
            return {
                "status": "success",
                "message": "Memori berhasil disimpan.",
                "data": {
                    "summary": final_summary
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Gagal menyimpan memori: {str(e)}"
            }
