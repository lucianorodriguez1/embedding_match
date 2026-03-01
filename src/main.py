import psycopg2
from psycopg2.extras import execute_values
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv # 1. Importar la librería

# 2. Cargar las variables del archivo .env
load_dotenv()
# --- CONFIGURACIÓN ---
# IMPORTANTE: Asegúrate de tener esta variable de entorno configurada
# o reemplaza os.getenv(...) por tu API KEY real entre comillas.
GOOGLE_API_KEY = os.getenv("GEMINIS_API_KEY") 
DB_CONFIG = {
    "host": "localhost",
    "database": "student_match",
    "user": "user",
    "password": "password",
    "port": "5432"
}

genai.configure(api_key=GOOGLE_API_KEY)

# --- FUNCIONES ---
def obtener_conexion():
    return psycopg2.connect(**DB_CONFIG)

def generar_embedding(texto):
    """Convierte texto en un vector numérico usando Gemini"""
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texto
    )
    return result['embedding']

def registrar_alumno(nombre, habilidades, descripcion):
    """Guarda al alumno y sus habilidades/descripción en vector en Postgres local"""
    # JUNTAMOS HABILIDADES Y DESCRIPCIÓN PARA MEJOR CONTEXTO
    texto_completo = f"Habilidades: {habilidades}. Descripción: {descripcion}"
    
    embedding = generar_embedding(texto_completo)
    
    conn = obtener_conexion()
    cur = conn.cursor()
    
    query = """
    INSERT INTO alumnos (nombre, habilidades, descripcion, habilidades_vector)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(query, (nombre, habilidades, descripcion, embedding))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Alumno {nombre} registrado localmente con contexto completo.")

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