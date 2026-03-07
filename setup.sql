-- Habilitar extensión de vectores
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS alumnos (
    dni VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100),
    habilidades TEXT,
    descripcion TEXT,
    habilidades_vector vector(384) 
);

CREATE TABLE IF NOT EXISTS proyectos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) UNIQUE,
    descripcion TEXT,
    descripcion_vector vector(384)
);