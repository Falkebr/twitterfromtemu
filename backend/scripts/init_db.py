from backend.database import engine, Base
import backend.models  # Import all models via __init__.py to register with Base

# Debug: print engine URL and tables
print(f"Engine URL: {engine.url}")
print(f"Tables to create: {Base.metadata.tables.keys()}")

# Create all tables in the database
Base.metadata.create_all(bind=engine)
print("All tables created.")
