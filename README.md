# 🚀 Local Talent Matcher con IA
Sistema de matching local para conectar estudiantes de la Licenciatura en Sistemas con proyectos reales, utilizando búsqueda semántica basada en embeddings generados por IA (Gemini API) y almacenados en PostgreSQL con pgvector. El sistema permite registrar perfiles de estudiantes y proyectos, y encontrar coincidencias relevantes según habilidades, intereses y descripciones, priorizando el aprendizaje y la colaboración.
- Ejemplo de la respuesta:
``` bash
🔍 Proyecto: Gestión de Turnos Médicos
🏆 Top 3 Candidatos:
  - Daniela Vázquez (66.27%) | Skills: Swift, iOS, CoreData
  - Romina Medina (65.64%) | Skills: Java, Android, SQLite
  - Julian Herrera (62.82%) | Skills: Java, Android, Firebase, Git

  ```


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
python -m venv .venv
.venv\Scripts\activate  # Activa el entorno virtual
pip install -r requeriments.txt
```

### 2. Configurar Variables de Entorno (.env)
Crea un archivo .env en la raíz del proyecto y agrega tu clave API:

```python
GEMINIS_API_KEY=tu_clave_api_aqui
DB_HOST=tu_host
DB_NAME=tu_db_name
DB_USER=tu_user
DB_PASS=tu_pass
DB_PORT=tu_port
```

### 3. Levantar la Base de Datos con Docker

```console
docker-compose up -d --build
```

### 4. Preparar la Base de Datos (SQL)

Conéctate a tu base de datos usando pgAdmin (CREÁ LA BASE DE DATOS CON EL NOMBRE QUE LE ASIGNASTE EN .ENV) o tu herramienta favorita y ejecuta el siguiente SQL:

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


## Conceptos

### Similitud del Coseno
En lugar de buscar palabras clave exactas (que fallan si uno pone "Python" y el otro "Programación en Django"), convertimos el texto en vectores numéricos. Si los vectores apuntan en la misma dirección, hay match.

## Implementacion

1. Normalización de datos:
Junta la descripción y los tags del alumno en un solo bloque de texto. Se hace lo mismo con la descripción del proyecto.

**Ejemplo** Alumno: "Juan, experto en React y Firebase, interesado en Fintech."

**Ejemplo** Proyecto: "Buscamos desarrollador Frontend para app de pagos con React."

2. Generación de Embeddings:
Envía esos textos a una API (como la de Gemini o OpenAI). Ellos te devolverán una lista de números (el vector).

Usa el modelo text-embedding-004 de Google, que es extremadamente barato y rápido.

3. Almacenamiento (Vector Database):
Guarda esos números en una base de datos que soporte vectores.

Opciones simples: Supabase (con pgvector) o Pinecone. Si estás en algo muy local, incluso una librería como FAISS sirve.

4. El Matching (La consulta):
Cuando se publica un proyecto:

    - Generas el vector del proyecto.

    - Le pides a tu DB: "Dame los 5 alumnos cuyos vectores sean más similares a este vector de proyecto".

    - El sistema te devolverá los IDs con un "score" de similitud (ej. 0.95 es match casi total).
