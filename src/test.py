import requests


TOKEN = "API_KEY"

# 2. Le quitamos cualquier espacio invisible por si acaso
TOKEN = TOKEN.strip()

API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"

print(f"Probando conexión con la llave: {TOKEN[:8]}...")

headers = {"Authorization": f"Bearer {TOKEN}"}
response = requests.post(API_URL, headers=headers, json={"inputs": "Probando si el cerebro funciona"})

if response.status_code == 200:
    print("✅ ¡ÉXITO TOTAL! Hugging Face aceptó tu llave.")
    print("Esto significa que la llave está perfecta y el problema era el archivo .env.")
else:
    print(f"❌ FALLÓ. Código de error: {response.status_code}")
    print(f"Respuesta de Hugging Face: {response.text}")