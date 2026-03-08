import json
import os
from src.repository.repository import registrar_alumno

def cargar_desde_json():
    # Asumimos que estás en la carpeta raiz del proyecto
    base_path = os.path.dirname(os.path.dirname(__file__)) 
    mocks_path = os.path.join(base_path, 'mocks')
    
    ruta_estudiantes = os.path.join(mocks_path, 'students.json')
    ruta_proyectos = os.path.join(mocks_path, 'projects.json')

    # Cargar Alumnos
    if os.path.exists(ruta_estudiantes):
        with open(ruta_estudiantes, 'r', encoding='utf-8') as f:
            alumnos = json.load(f)
            for a in alumnos:
                registrar_alumno(a['dni'], a['nombre'], a['habilidades'], a['descripcion'])
    
    # Cargar Proyectos
    if os.path.exists(ruta_proyectos):
        with open(ruta_proyectos, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []