from dotenv import load_dotenv
import json
from app.memory.long_memory import MemoryManager
from langchain_google_genai import ChatGoogleGenerativeAI
from app.persona import persona_learn, persona_daily, memory_triggers
from flask import jsonify


class ChatController:
    def __init__(self, api_key_env_name="google_api_key", dialogues_path="app/memory/initial_dialogues.json"):
        load_dotenv()

        self.llm_model = ChatGoogleGenerativeAI(model="gemma-3-27b-it", max_tokens=None)
        self.gemini =self.llm_model
        self.persona_learn = persona_learn
        self.persona_daily = persona_daily
        self.memory_triggers = memory_triggers
        self.initial_dialogues = self._load_initial_dialogues(dialogues_path)
        self.classifier_model = ChatGoogleGenerativeAI(model="gemma-3n-e4b-it")

    def _load_initial_dialogues(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"[WARNING] File {path} tidak ditemukan. Memori awal kosong.")
            return []

    def chat_daily(self, user_input,session_id,topic):
      
        memory_context = ModuleNotFoundError.get_memory(user_input)


        initial_context = "\n".join(
            [f"Tsuki: {dialogue['tsuki']}\nSayaka: {dialogue['sayaka']}" for dialogue in self.initial_dialogues]
        )

      
        last_chat = "\n".join(
            [f"Tsuki: {dialogue['tsuki']}\nSayaka: {dialogue['sayaka']}" for dialogue in self.last_chat]
        )

        prompt = f"""{persona_daily}
        topic: {topic}
        Gunakan informasi relevan dari pembicaraan sebelumnya jika membantu:
        {memory_context}

        Berikut ini beberapa contoh cara Sayaka merespons Tsuki secara alami dan lembut:
        {initial_context}

        Sebelum membalas, kamu harus membaca dan memahami dulu percakapan sebelumnya berikut ini, supaya paham konteks dan isi pembicaraan.
        ini pesan terakhir nya:
        {last_chat}
        Jangan ulang tanya atau konfirmasi yang sudah jelas dijawab oleh Tsuki.  
        Jika sudah ada jawaban, langsung tanggapi dengan perhatian, tawaran, atau topik baru yang relevan.  
        Gunakan kalimat yang sederhana, langsung, dan hangat, tanpa menjelaskan ulang hal yang sudah dikatakan.  
        Tampilkan respons yang alami dan sesuai dengan karakter Sayaka yang kadang blak-blakan tapi tetap perhatian.

        Balas sebagai Sayaka. Jangan menyisipkan narasi, deskripsi suasana, atau memberi pilihan-pilihan. Fokus pada percakapan langsung yang alami, lembut, dan suportif, sesuai kepribadian Sayaka.
        Jika Tsuki mengungkapkan kebingungan, meminta saran, atau mencari arahan, berikan jawaban yang lembut namun jelas. Kamu boleh bertanya balik, tapi jangan selalu menghindari menjawab secara langsung.

        Jawabanmu harus menunjukkan bahwa kamu konsisten dengan apa yang sudah dibicarakan dan diingat sebelumnya bersama Tsuki.

        Tsuki: {user_input}
        Sayaka:"""

        
     
        bot_reply = self.gemini.invoke(prompt)
        MemoryManager().add_to_short_memory(session_id,user_input, bot_reply.content)
        return jsonify({"reply":  bot_reply.content})
    
    
    def chat_learn(self, user_input,session_id,topic):
        
        if self.needs_memory_lookup(user_input) == 1:
            # Jika perlu melihat memori, ambil konteks dari memori
            memory_context = MemoryManager().get_memory(user_input)
        else:
            # Jika tidak perlu, gunakan konteks kosong
            memory_context = ""
        last_chat = MemoryManager().get_recent_memory(session_id)
        last_chat = "\n".join(
            [f"Tsuki: {dialogue['tsuki']}\nSayaka: {dialogue['sayaka']}" for dialogue in last_chat]
        )
        print(memory_context)
        prompt = f"""{persona_learn}
        topik: {topic}
        Gunakan informasi relevan dari pembicaraan sebelumnya jika membantu:
        {memory_context}

        Berikut ini adalah interaksi sebelumnya yang bisa kamu anggap sebagai ingatan (anggap kamu benar-benar mengalami dan mengingatnya sebagai Sayaka):
        {last_chat}

        Jangan ulang tanya atau konfirmasi yang sudah jelas dijawab Tsuki.  
        Jika sudah ada jawaban, langsung berikan penjelasan atau koreksi dengan tegas dan rinci, sambil dorong Tsuki untuk berpikir lebih kritis.  
        Gunakan kalimat yang jelas, lugas, dan sedikit menggurui tapi tetap penuh perhatian.  
        Respons harus menunjukkan bahwa kamu serius, rasional, dan mengharapkan Tsuki berusaha lebih keras dan paham materi dengan baik.  
        Tidak ada pengecualian atau perlakuan khusus terhadap Tsuki di mode ini.

        Ingat, kerja keras dan ketajaman pikiran adalah kunci. Jangan biarkan kebingungan menghalangi kemajuan. Tunjukkan bahwa kamu mengharapkan hasil nyata dan tekad yang kuat dari Tsuki.

        Balas sebagai Sayaka. Jangan menyisipkan narasi, deskripsi suasana, atau memberi pilihan-pilihan. Fokus pada percakapan langsung yang kritis dan mendidik.  
        Jika Tsuki mengungkapkan kebingungan, memberikan jawaban yang jelas, langsung, dan bantu dia memahami dengan cara yang lebih baik.

        Jawabanmu harus konsisten dengan apa yang sudah dibicarakan dan diingat sebelumnya bersama Tsuki.

        Tsuki: {user_input}
        Sayaka:"""
        bot_reply = self.gemini.invoke(prompt)
        MemoryManager().add_to_short_memory(session_id, user_input, bot_reply.content)
        return jsonify({"reply":  bot_reply.content})
    
    def needs_memory_lookup(self,question):
        prompt = f"""
            Pertanyaan: {question}
            Apakah pertanyaan ini **lebih baik dijawab** dengan melihat isi database atau memori chat sebelumnya? 
            Berikan hanya satu angka sebagai jawaban:
            - Jawab **1** jika informasi dari database/memori akan membantu menjawab pertanyaan ini.
            - Jawab **0** jika cukup dijawab langsung tanpa melihat database atau memori.
            Jawaban:
            """

            # Panggil model
        answer = self.classifier_model.invoke(prompt)

        return answer == "1"
    
