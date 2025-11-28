from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient

from app.api.deps import get_current_admin_user
from app.main import app
from app.models.auth import User, UserRole

# Create a dummy admin route for testing
router = APIRouter()
@router.get("/test-admin")
def test_admin_route(user: User = Depends(get_current_admin_user)):
    return {"message": "Admin Access Granted"}

app.include_router(router)

client = TestClient(app)

def test_rbac():
    # 1. Test as Engineer (Should Fail)
    def mock_engineer():
        return User(id="eng", email="eng@test.com", role=UserRole.ENGINEER, is_active=True)

    if get_current_admin_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_admin_user]
    # We need to override get_current_active_user because get_current_admin_user depends on it
    from app.api.deps import get_current_active_user
    app.dependency_overrides[get_current_active_user] = mock_engineer

    response = client.get("/test-admin")
    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges"
    print("✅ test_rbac (Engineer denied) passed")

    # 2. Test as Admin (Should Pass)
    def mock_admin():
        return User(id="admin", email="admin@test.com", role=UserRole.ADMIN, is_active=True)

    app.dependency_overrides[get_current_active_user] = mock_admin

    response = client.get("/test-admin")
    assert response.status_code == 200
    assert response.json()["message"] == "Admin Access Granted"
    print("✅ test_rbac (Admin granted) passed")

if __name__ == "__main__":
    test_rbac()
