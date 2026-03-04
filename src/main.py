import psycopg2
from psycopg2.extras import execute_values
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv 

# 1. Importar la librería

# 2. Cargar las variables del archivo .env
load_dotenv()

# --- CONFIGURACIÓN ---
# IMPORTANTE: Asegúrate de tener esta variable de entorno configurada
GOOGLE_API_KEY = os.getenv("GEMINIS_API_KEY") 
DB_CONFIG = {
    "host": "localhost",
    "database": "student_match",
    "user": "user",
    "password": "password",
    "port": "5432"
}

genai.configure(api_key=GOOGLE_API_KEY)

# --- TRACKING DE RECURSOS ---
stats = {"total_tokens": 0, "api_calls": 0}


def registrar_metricas(texto):
    global stats
    # Estimación: Gemini usa BPE, aprox 1 token cada 4 caracteres
    tokens = len(texto) // 4 
    stats["api_calls"] += 1
    stats["total_tokens"] += tokens
    return tokens

# --- FUNCIONES ---
def obtener_conexion():
    return psycopg2.connect(**DB_CONFIG)

def generar_embedding(texto):
    registrar_metricas(texto)
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texto
    )
    return result['embedding']


def registrar_alumno(dni, nombre, habilidades, descripcion):
    texto_completo = f"Habilidades: {habilidades}. Descripción: {descripcion}"
    embedding = generar_embedding(texto_completo)
    
    conn = obtener_conexion()
    cur = conn.cursor()
    try:
        # Usamos DNI para el ON CONFLICT
        query = """
        INSERT INTO alumnos (dni, nombre, habilidades, descripcion, habilidades_vector)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (dni) DO NOTHING;
        """
        cur.execute(query, (dni, nombre, habilidades, descripcion, embedding))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def buscar_candidatos(proyecto_descripcion):
    embedding_proyecto = generar_embedding(proyecto_descripcion)
    
    conn = obtener_conexion()
    cur = conn.cursor()
    try:
        query = """
        SELECT nombre, habilidades, 1 - (habilidades_vector <=> %s::vector) AS similitud
        FROM alumnos
        ORDER BY similitud DESC LIMIT 5;
        """
        cur.execute(query, (embedding_proyecto,))
        resultados = cur.fetchall()
        return resultados # Retornamos los datos
    finally:
        # IMPORTANTE: Cerramos SIEMPRE, incluso si hay error
        cur.close()
        conn.close()

def cargar_desde_json():
    """Carga alumnos y proyectos usando rutas relativas al script"""
    # Obtenemos la carpeta donde está main.py (src/)
    base_path = os.path.dirname(__file__) 
    # Construimos la ruta hacia la carpeta mocks
    mocks_path = os.path.join(base_path, 'mocks')
    
    ruta_estudiantes = os.path.join(mocks_path, 'students.json')
    ruta_proyectos = os.path.join(mocks_path, 'projects.json')

    # 1. Cargar Alumnos
    if os.path.exists(ruta_estudiantes):
        with open(ruta_estudiantes, 'r', encoding='utf-8') as f:
            alumnos = json.load(f)
            for a in alumnos:
                registrar_alumno(a['dni'], a['nombre'], a['habilidades'], a['descripcion'])
        print(f"✅ Se procesaron {len(alumnos)} alumnos del JSON.")
    else:
        print(f"❌ Error: No se encontró {ruta_estudiantes}")

    # 2. Retornar Proyectos para probar
    if os.path.exists(ruta_proyectos):
        with open(ruta_proyectos, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"❌ Error: No se encontró {ruta_proyectos}")
    
    return []


   # --- EJECUCIÓN ---
if __name__ == "__main__":
    print("🚀 Iniciando sistema Student Match...")
    
    # 1. Cargar datos de prueba (Mocks)
    proyectos_prueba = cargar_desde_json()
    
    # 2. Ejecutar búsqueda para cada proyecto del JSON
    print("\n--- EJECUTANDO PRUEBAS DE MATCHING ---")
    
    for proy in proyectos_prueba:
        print(f"\n🔍 Proyecto: {proy['titulo']}")
        print(f"📄 Requerimientos: {proy['descripcion'][:80]}...")
        
        candidatos = buscar_candidatos(proy['descripcion'])
        
        print(f"🏆 Top 3 Candidatos:")
        for c in candidatos[:3]: # Mostramos los 3 mejores
            # c[0]: nombre, c[1]: habilidades, c[2]: similitud
            print(f"  - {c[0]} (Similitud: {c[2]:.2%}) | Skills: {c[1]}")

    # 3. Mostrar límites del modelo
    print("\n--- LÍMITES DEL MODELO GEMINI EMBEDDING 1 ---")
    print("Tipo de Límite                Valor Máximo")
    print("Tokens por Petición Individual 2,048 tokens")
    print("Tokens por Minuto (TPM)        30,000 tokens")
    print("Solicitudes por Minuto (RPM)   100 solicitudes")
    print("Solicitudes por Día (RPD)      1,000 solicitudes")
    print("Puedes consultar estas métricas y límites para evitar errores de cuota o sobrecarga.")

    # 4. Mostrar Métricas Finales
    print("\n" + "="*30)
    print("📊 MÉTRICAS DE CONSUMO API")
    print(f"Llamadas totales: {stats['api_calls']}")
    print(f"Tokens estimados: {stats['total_tokens']}")
    # Los embeddings de Gemini son gratuitos en el plan básico (hasta 1500 RPM)
    print("Costo real estimado: $0.00 USD")
    print("="*30)

# --- LÍMITES DEL MODELO GEMINI EMBEDDING 1 ---
# Estos son los límites oficiales para el modelo de vectores usado en este sistema:
#
# Tipo de Límite                Valor Máximo
# Tokens por Petición Individual 2,048 tokens
# Tokens por Minuto (TPM)        30,000 tokens
# Solicitudes por Minuto (RPM)   100 solicitudes
# Solicitudes por Día (RPD)      1,000 solicitudes

# Puedes consultar estas métricas y límites para evitar errores de cuota o sobrecarga.