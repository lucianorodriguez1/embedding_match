-- 1. Habilitar la extensión para guardar vectores (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Crear la tabla de alumnos
-- Usamos 768 dimensiones porque es lo que usa el modelo text-embedding-004 de Gemini
CREATE TABLE IF NOT EXISTS alumnos (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  habilidades TEXT,
  descripcion TEXT,
  habilidades_vector VECTOR(768)
);