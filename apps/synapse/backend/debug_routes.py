
from app.main import app

print("Registered Routes:")
for route in app.routes:
    print(f"{route.methods} {route.path} -> {route.name}")
