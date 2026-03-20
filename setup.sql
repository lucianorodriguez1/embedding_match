-- 1. Habilitar la extensión para guardar vectores (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Crear la tabla de alumnos
-- Usamos 3072 dimensiones porque es lo que usa el modelo text-embedding-004 de Gemini
CREATE TABLE IF NOT EXISTS alumnos (
    dni VARCHAR(20) PRIMARY KEY, -- El DNI es ahora la clave única
    nombre VARCHAR(100),
    habilidades TEXT,
    descripcion TEXT,
    habilidades_vector vector(3072) -- Dimensión para Gemini
);

CREATE TABLE IF NOT EXISTS proyectos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) UNIQUE,
    descripcion TEXT,
    descripcion_vector vector(3072)
);

