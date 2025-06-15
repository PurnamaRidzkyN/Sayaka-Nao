from typing import List
import re

def chunk_text( text: str) -> List[str]:
    chunks = []
    buffer = ""
    max_chunk_size = 300  
    
    # Hapus tanda aneh (non-ASCII kecuali spasi dan tanda baca dasar)
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # Hapus karakter non-ASCII
    text = re.sub(r"[^\w\s.,!?;:'\"()\[\]{}\-]", "", text)  # Hapus simbol aneh lainnya

    i = 0
    while i < len(text):
        buffer += text[i]
        i += 1

        # Kalau sudah lewat batas dan ada titik → potong
        if len(buffer) >= max_chunk_size:
            # Cek kalau ada titik di buffer
            if '.' in buffer:
                last_dot = buffer.rfind('.') + 1  # Ambil sampai setelah titik
                chunks.append(buffer[:last_dot].strip())
                buffer = buffer[last_dot:]  # Sisakan sisanya ke buffer baru

    # Masukkan sisa akhir kalau ada
    if buffer.strip():
        chunks.append(buffer.strip())

    return chunks