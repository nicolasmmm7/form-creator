# tests/conftest.py
"""

mongomock simula MongoDB 
"""
import pytest
import mongoengine
import mongomock


@pytest.fixture(autouse=True)
def mongo_connection():
    """
    Fixture que conecta a una BD MongoDB simulada (mongomock)
    antes de cada prueba y la desconecta al finalizar.
    
    autouse=True → se aplica automáticamente a TODAS las pruebas.
    """
    # Desconectar cualquier conexión previa (evita conflictos con settings.py)
    mongoengine.disconnect_all()
    
    # Conectar a mongomock (BD en memoria)
    # IMPORTANTE: pasar la CLASE directamente, no un string
    conn = mongoengine.connect(
        db='test_formcreator',
        host='mongodb://localhost',
        mongo_client_class=mongomock.MongoClient  # ← Clase, NO string
    )
    
    yield conn  # La prueba se ejecuta aquí
    
    # Limpiar: eliminar toda la data y desconectar
    db = mongoengine.get_db()
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
    
    mongoengine.disconnect_all()
