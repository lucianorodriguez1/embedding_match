import psycopg2
from psycopg2.extras import execute_values
import json
import os
import requests
from dotenv import load_dotenv 


# 2. Cargar las variables del archivo .env
load_dotenv(override=True)
# --- CONFIGURACIÓN ---
# IMPORTANTE: Asegurate de tener esta variable de entorno configurada
# o reemplaza os.getenv(...) por tu API KEY real entre comillas.
HF_KEYS = [
    os.getenv("HF_KEY_1"),
    os.getenv("HF_KEY_2"),
    os.getenv("HF_KEY_3")
]
# Filtramos las llaves que estén vacías en .env(por si solo se pusieron 1 o 2)
HF_KEYS = [key for key in HF_KEYS if key]

# Modelo elegido: all-MiniLM-L6-v2 
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}/pipeline/feature-extraction"

DB_CONFIG = {
    "host": "127.0.0.1",
    "database": "student_match",
    "user": "user",
    "password": "password",
    "port": "5433"
}

def obtener_conexion():
    return psycopg2.connect(**DB_CONFIG)

def generar_embedding(texto):
    """
    Intenta generar el vector iterando por las API keys de Hugging Face.
    """
    if not HF_KEYS:
        raise ValueError("No hay API Keys de Hugging Face configuradas en el .env")

    for indice, key in enumerate(HF_KEYS):
        headers = {"Authorization": f"Bearer {key}"}
        payload = {"inputs": texto}
        
        try:
            print(f"Intentando con Llave {indice + 1}...")
            response = requests.post(API_URL, headers=headers, json=payload)
            
            # Si el código es 200, todo salió perfecto
            if response.status_code == 200:
                return response.json()
                
            # Si es 429 (Too Many Requests) o 503 (Model Loading/Saturado), saltamos
            elif response.status_code in [429, 503]:
                print(f"⚠️ Llave {indice + 1} saturada o sin tokens (Error {response.status_code}).")
                continue # Pasa a la siguiente llave en el for loop
            else:
                print(f"Error inesperado con la Llave {indice + 1}: {response.text}")
                continue
                
        except Exception as e:
            print(f"Fallo de conexión en la Llave {indice + 1}: {e}")
            continue
            
    # Si el bucle termina y no retornó nada, todas las llaves fallaron
    raise Exception("🚨 Todas las llaves del carrusel fallaron o están sin límite.")

def registrar_alumno(nombre, habilidades, descripcion):
    print(f"\nRegistrando a {nombre}...")
    texto_completo = f"Habilidades: {habilidades}. Descripción: {descripcion}"
    
    try:
        embedding = generar_embedding(texto_completo)
        
        conn = obtener_conexion()
        cur = conn.cursor()
        
        query = """
            INSERT INTO alumnos (nombre, habilidades, descripcion, habilidades_vector)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (nombre, habilidades, descripcion, embedding))
        conn.commit()
        print(f"✅ ¡{nombre} registrado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al registrar: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        
def buscar_candidatos(proyecto_descripcion):
    """Busca candidatos usando similitud vectorial en Postgres local"""
    embedding_proyecto = generar_embedding(proyecto_descripcion)
    
    conn = obtener_conexion()
    cur = conn.cursor()
    
    # Similitud del coseno: 1 - (vector <=> embedding)
    query = """
    SELECT nombre, habilidades, descripcion,
           1 - (habilidades_vector <=> %s::vector) AS similitud
    FROM alumnos
    ORDER BY similitud DESC
    LIMIT 5;
    """
    cur.execute(query, (embedding_proyecto,))
    resultados = cur.fetchall()
    
    cur.close()
    conn.close()
    return resultados


# --- EJECUCIÓN (Ejemplos Completos) ---
if __name__ == "__main__":
    # 1. Registrar alumnos (SOLO EJECUTAR ESTO UNA VEZ)
    print("Registrando alumnos...")
    
    registrar_alumno(
        "Juan", 
        "Python, Django, SQL, PostgreSQL", 
        "Desarrollador Backend con 2 años de experiencia en Fintech buscando proyectos desafiantes en sistemas de pago."
    )
    
    registrar_alumno(
        "Maria", 
        "Figma, React, UX, UI", 
        "Diseñadora frontend enfocada en usabilidad y accesibilidad web. Experta en crear interfaces intuitivas."
    )
    
    registrar_alumno(
        "Pedro", 
        "Node.js, Express, MongoDB", 
        "Desarrollador Fullstack junior con interés en crear APIs rápidas y escalables usando tecnologías modernas."
    )
    
    registrar_alumno(
        "Ana", 
        "Python, FastApi, Docker, Kubernetes", 
        "Ingeniera DevOps con sólida experiencia en backend Python y despliegue de microservicios en la nube."
    )
    
    registrar_alumno(
        "Luis", 
        "React, Angular, TypeScript", 
        "Desarrollador Frontend Senior con 5 años de experiencia liderando equipos técnicos."
    )
    
    print("Alumnos registrados.\n")

    # 2. Buscar candidatos para un proyecto complejo
    print("Buscando candidatos para el proyecto...")
    proyecto = "Buscamos desarrollador Backend experto en Python para microservicio de transacciones financieras. Necesitamos conocimientos en SQL y despliegue en contenedores."
    
    candidatos = buscar_candidatos(proyecto)
    
    print(f"\n--- Resultados del Proyecto: '{proyecto}' ---")
    print("Candidatos encontrados (Nombre, Similitud):")
    for c in candidatos:
        # Imprimimos nombre y similitud (c[0] es nombre, c[3] es similitud)
        print(f"- {c[0]} (Similitud: {c[3]:.2f})")