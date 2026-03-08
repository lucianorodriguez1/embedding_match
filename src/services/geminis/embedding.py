import google.generativeai as genai
import os
from src.services.geminis.metrics import registrar_metricas

genai.configure(api_key=os.getenv("GEMINIS_API_KEY"))

def generar_embedding(texto):
    registrar_metricas(texto)
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texto
    )
    return result['embedding']

# Aquí irá en el futuro tu función de Gemini 1.5 Flash para los mensajes batch