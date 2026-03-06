

-- Habilitar extensión de vectores
CREATE EXTENSION IF NOT EXISTS vector;

-- Crear tabla con múltiples columnas vectoriales para diferentes modelos de ia 
CREATE TABLE alumnos (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  habilidades TEXT,
  descripcion TEXT,
  gemini_vector VECTOR(3072),   -
);