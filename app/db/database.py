import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from the .env file.
# Carga las variables de entorno desde el archivo .env.
load_dotenv()

# Read the PostgreSQL connection string from the environment.
# Lee la cadena de conexión a PostgreSQL desde el entorno.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

# Create the SQLAlchemy engine used to connect to PostgreSQL.
# Crea el motor de SQLAlchemy usado para conectarse a PostgreSQL.
engine = create_engine(DATABASE_URL)

# Create a database session factory for the application.
# Crea una fábrica de sesiones de base de datos para la aplicación.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class used by all SQLAlchemy models.
# Clase base usada por todos los modelos de SQLAlchemy.
Base = declarative_base()
