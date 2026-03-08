from src.config.db.connect import obtener_conexion
from src.services.geminis.embedding import generar_embedding

def registrar_alumno(dni, nombre, habilidades, descripcion):
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM alumnos WHERE dni = %s", (dni,))
            if cur.fetchone(): return
            
            embedding = generar_embedding(f"Habilidades: {habilidades}. {descripcion}")
            query = """
                INSERT INTO alumnos (dni, nombre, habilidades, descripcion, habilidades_vector)
                VALUES (%s, %s, %s, %s, %s) ON CONFLICT (dni) DO NOTHING;
            """
            cur.execute(query, (dni, nombre, habilidades, descripcion, embedding))
            conn.commit()

def registrar_proyecto(id_proy, titulo, desc):
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT descripcion_vector FROM proyectos WHERE id = %s", (id_proy,))
            res = cur.fetchone()
            if res: return res[0]
            
            print(f"✨ Vectorizando nuevo proyecto: {titulo}")
            vector = generar_embedding(desc)
            cur.execute("""
                INSERT INTO proyectos (id, titulo, descripcion, descripcion_vector)
                VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;
            """, (id_proy, titulo, desc, vector))
            conn.commit()
            return vector

def buscar_candidatos(vector_proyecto):
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT nombre, habilidades, 1 - (habilidades_vector <=> %s::vector) AS similitud
                FROM alumnos ORDER BY similitud DESC LIMIT 5;
            """
            cur.execute(query, (vector_proyecto,))
            return cur.fetchall()