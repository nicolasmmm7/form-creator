import sys
import os
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock django settings
from django.conf import settings
if not settings.configured:
    settings.configure(INSTALLED_APPS=['usuarioapp'])

# Mock mongoengine and models BEFORE importing serializers
import sys
from unittest.mock import MagicMock

# Create mock classes for models
class MockUsuarioObjects:
    def __init__(self):
        self.existing_emails = ["existing@example.com"]

    def __call__(self, email=None):
        self.current_query_email = email
        return self

    def first(self):
        if self.current_query_email in self.existing_emails:
            return MagicMock() # Return a mock object if email exists
        return None

class MockUsuario:
    objects = MockUsuarioObjects()
    DoesNotExist = Exception

# Patch the modules in sys.modules
sys.modules['usuarioapp.models'] = MagicMock()
sys.modules['usuarioapp.models'].Usuario = MockUsuario
sys.modules['usuarioapp.models'].Empresa = MagicMock()
sys.modules['usuarioapp.models'].Perfil = MagicMock()

# Now import the serializer
from usuarioapp.serializers import UsuarioSerializer
from rest_framework.exceptions import ValidationError

def run_verification():
    print("Running verification for UsuarioSerializer.validate_email...")
    
    serializer = UsuarioSerializer()
    
    # Test 1: New email (should pass)
    try:
        email = "new@example.com"
        result = serializer.validate_email(email)
        print(f"✅ Test 1 Passed: Email '{email}' is valid.")
    except ValidationError as e:
        print(f"❌ Test 1 Failed: {e}")

    # Test 2: Existing email (should fail)
    try:
        email = "existing@example.com"
        serializer.validate_email(email)
        print(f"❌ Test 2 Failed: Email '{email}' should have raised ValidationError.")
    except ValidationError as e:
        print(f"✅ Test 2 Passed: Email '{email}' raised ValidationError as expected.")

    print("Verification complete.")

if __name__ == "__main__":
    run_verification()
