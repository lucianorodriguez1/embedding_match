import psycopg2
import json
import os
import requests
import time
from dotenv import load_dotenv 

# 1. Cargar las variables del archivo .env
load_dotenv(override=True)

# --- CONFIGURACIÓN ---
# Cargamos las llaves del .env y filtramos las vacías
HF_KEYS = [
    os.getenv("HF_KEY_1"),
    os.getenv("HF_KEY_2"),
    os.getenv("HF_KEY_3")
]
HF_KEYS = [key for key in HF_KEYS if key]

# Modelo elegido: all-MiniLM-L6-v2 (Genera vectores de 384 dimensiones)
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}/pipeline/feature-extraction"

DB_CONFIG = {
    "host": "127.0.0.1",
    "database": "student_match",
    "user": "user",
    "password": "password",
    "port": "5433"
}

# --- TRACKING DE RECURSOS ---
stats = {"total_tokens": 0, "api_calls": 0}

def registrar_metricas(texto):
    global stats
    # Estimación para MiniLM: aprox 1 token por cada palabra y media (usamos 1.3 de multiplicador)
    tokens = int(len(texto.split()) * 1.3) 
    stats["api_calls"] += 1
    stats["total_tokens"] += tokens
    return tokens

# --- FUNCIONES ---

def obtener_conexion():
    return psycopg2.connect(**DB_CONFIG)

def generar_embedding(texto):
    """
    Intenta generar el vector iterando por las API keys de Hugging Face.
    """
    if not HF_KEYS:
        raise ValueError("No hay API Keys de Hugging Face configuradas en el .env")

    registrar_metricas(texto)

    for indice, key in enumerate(HF_KEYS):
        headers = {"Authorization": f"Bearer {key}"}
        payload = {"inputs": texto}
        
        try:
            # Pequeña pausa para no saturar la API gratuita de golpe
            time.sleep(0.5) 
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                # La API de HF suele devolver una lista o lista de listas. Extraemos el vector plano.
                resultado = response.json()
                # Si es una lista de listas (ej. [[0.1, 0.2...]]), sacamos la primera
                if isinstance(resultado, list) and isinstance(resultado[0], list):
                    return resultado[0]
                return resultado
                
            elif response.status_code in [429, 503]:
                print(f"⚠️ Llave {indice + 1} saturada o modelo cargando (Error {response.status_code}).")
                continue 
            else:
                print(f"Error inesperado con la Llave {indice + 1}: {response.text}")
                continue
                
        except Exception as e:
            print(f"Fallo de conexión en la Llave {indice + 1}: {e}")
            continue
            
    raise Exception("🚨 Todas las llaves del carrusel fallaron o están sin límite.")

def registrar_alumno(dni, nombre, habilidades, descripcion):
    print(f"\nRegistrando a {nombre}...")
    texto_completo = f"Habilidades: {habilidades}. Descripción: {descripcion}"
    
    try:
        embedding = generar_embedding(texto_completo)
        
        conn = obtener_conexion()
        cur = conn.cursor()
        
        # Usamos DNI para el ON CONFLICT y evitar duplicados
        query = """
        INSERT INTO alumnos (dni, nombre, habilidades, descripcion, habilidades_vector)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (dni) DO NOTHING;
        """
        cur.execute(query, (dni, nombre, habilidades, descripcion, embedding))
        conn.commit()
        print(f"✅ ¡{nombre} registrado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al registrar {nombre}: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def buscar_candidatos(proyecto_descripcion):
    embedding_proyecto = generar_embedding(proyecto_descripcion)
    
    conn = obtener_conexion()
    cur = conn.cursor()
    try:
        # <=> es el operador de pgvector para Similitud del Coseno
        query = """
        SELECT nombre, habilidades, 1 - (habilidades_vector <=> %s::vector) AS similitud
        FROM alumnos
        ORDER BY similitud DESC LIMIT 5;
        """
        cur.execute(query, (embedding_proyecto,))
        resultados = cur.fetchall()
        return resultados 
    finally:
        cur.close()
        conn.close()

def cargar_desde_json():
    """Carga alumnos y proyectos usando rutas relativas al script"""
    base_path = os.path.dirname(__file__) 
    mocks_path = os.path.join(base_path, 'mocks')
    
    ruta_estudiantes = os.path.join(mocks_path, 'students.json')
    ruta_proyectos = os.path.join(mocks_path, 'projects.json')

    if os.path.exists(ruta_estudiantes):
        with open(ruta_estudiantes, 'r', encoding='utf-8') as f:
            alumnos = json.load(f)
            for a in alumnos:
                # Asegurate de que tu JSON tenga el campo 'dni'
                registrar_alumno(a.get('dni', 0), a['nombre'], a['habilidades'], a['descripcion'])
        print(f"✅ Se procesaron {len(alumnos)} alumnos del JSON.")
    else:
        print(f"❌ Error: No se encontró {ruta_estudiantes}")

    if os.path.exists(ruta_proyectos):
        with open(ruta_proyectos, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"❌ Error: No se encontró {ruta_proyectos}")
    
    return []

# --- EJECUCIÓN ---
if __name__ == "__main__":
    print("🚀 Iniciando sistema Student Match...")
    
    proyectos_prueba = cargar_desde_json()
    
    print("\n--- EJECUTANDO PRUEBAS DE MATCHING ---")
    
    for proy in proyectos_prueba:
        print(f"\n🔍 Proyecto: {proy['titulo']}")
        print(f"📄 Requerimientos: {proy['descripcion'][:80]}...")
        
        candidatos = buscar_candidatos(proy['descripcion'])
        
        print(f"🏆 Top 3 Candidatos:")
        for c in candidatos[:3]:
            print(f"  - {c[0]} (Similitud: {c[2]:.2%}) | Skills: {c[1]}")

    # --- LÍMITES ACTUALIZADOS ---
    print("\n" + "="*50)
    print("--- LÍMITES DEL MODELO ALL-MINILM-L6-V2 (Hugging Face) ---")
    print("Tipo de Límite                 Valor Máximo")
    print("Tokens por Petición Individual ~256 tokens (aprox 180 palabras)")
    print("Límite de API Gratuita         Dinámico (Bloqueo por ráfagas)")
    print("Costo                          100% Gratuito")
    print("="*50)

    print("\n📊 MÉTRICAS DE CONSUMO API")
    print(f"Llamadas totales a HF: {stats['api_calls']}")
    print(f"Tokens enviados (aprox): {stats['total_tokens']}")
    print("="*50)