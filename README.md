# 🚀 Local Talent Matcher con IA
Este proyecto es un sistema local para registrar talento (habilidades/descripciones) y buscar a los mejores candidatos para un proyecto usando Búsqueda Semántica (Vector Search) con PostgreSQL y Gemini API.

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**: Lenguaje principal.
- **PostgreSQL**: Base de datos relacional.
- **pgvector**: Extensión de PostgreSQL para búsqueda vectorial.
- **Docker & Docker Compose**: Para levantar la base de datos fácilmente.
- **Google Gemini API**: Para generar los embeddings (vectores) de texto.
- **psycopg2**: Conector de Python para PostgreSQL.

## ⚙️ Configuración y Ejecución

### 1. Clonar el repositorio y configurar entorno

```console
git clone <https://github.com/lucianorodriguez1/embedding_match.git>
cd llm-python
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install psycopg2 google-generativeai python-dotenv
```

### 2. Configurar Variables de Entorno (.env)
Crea un archivo .env en la raíz del proyecto y agrega tu clave API:

```python
GEMINIS_API_KEY=tu_clave_api_aqui
```

### 3. Levantar la Base de Datos con Docker

```console
docker-compose up -d --build
```

### 4. Preparar la Base de Datos (SQL)

Conéctate a tu base de datos (localhost:5432, usuario user, contraseña password, db student_match) usando pgAdmin o tu herramienta favorita y ejecuta el siguiente SQL:

```sql
-- Habilitar extensión de vectores
CREATE EXTENSION IF NOT EXISTS vector;

-- Crear tabla de alumnos con 3072 dimensiones (modelo gemini-embedding-001)
CREATE TABLE IF NOT EXISTS alumnos (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  habilidades TEXT,
  descripcion TEXT,
  habilidades_vector VECTOR(3072)
);
```
5. Ejecutar la Aplicación
```console
python src/main.py

```

## 🧠 ¿Cómo funciona la búsqueda semántica?
* **Registro**: Almacenamos el nombre y descripción del talento. El texto de habilidades y descripción se envía a la API de Gemini, la cual devuelve una lista de 3072 números (un vector) que representa el significado de ese texto. Este vector se guarda en la BD.
* **Búsqueda**: Cuando buscas "Desarrollador backend para pagos", convertimos esa frase en un vector y le pedimos a PostgreSQL que busque los vectores de talento más cercanos al vector de búsqueda (similitud del coseno).

## ⚠️ Notas Importantes
* El script src/main.py tiene ejemplos de uso en la sección if __name__ == "__main__":.
* Asegúrate de no subir el archivo .env a control de versiones.

## Conceptos

### Similitud del Coseno
En lugar de buscar palabras clave exactas (que fallan si uno pone "Python" y el otro "Programación en Django"), convertimos el texto en vectores numéricos. Si los vectores apuntan en la misma dirección, hay match.

## Implementacion

1. Normalización de datos:
Junta la descripción y los tags del alumno en un solo bloque de texto. Haz lo mismo con la descripción del proyecto.

**Ejemplo** Alumno: "Juan, experto en React y Firebase, interesado en Fintech."

**Ejemplo** Proyecto: "Buscamos desarrollador Frontend para app de pagos con React."

2. Generación de Embeddings:
Envía esos textos a una API (como la de Gemini o OpenAI). Ellos te devolverán una lista de números (el vector).

Usa el modelo text-embedding-004 de Google, que es extremadamente barato y rápido.

3. Almacenamiento (Vector Database):
Guarda esos números en una base de datos que soporte vectores.

Opciones simples: Supabase (con pgvector) o Pinecone. Si estás en algo muy local, incluso una librería como FAISS te sirve.

4. El Matching (La consulta):
Cuando se publica un proyecto:

Generas el vector del proyecto.

Le pides a tu DB: "Dame los 5 alumnos cuyos vectores sean más similares a este vector de proyecto".

El sistema te devolverá los IDs con un "score" de similitud (ej. 0.95 es match casi total).