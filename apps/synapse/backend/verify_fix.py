
import requests

API_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{API_URL}/auth/login"
CLEAR_URL = f"{API_URL}/mock/project-data"
IMPORT_URL = f"{API_URL}/import_export/dev-import"
ASSETS_URL = f"{API_URL}/assets"

def verify():
    # 1. Login
    print("Logging in...")
    session = requests.Session()
    response = session.post(LOGIN_URL, data={"username": "admin@aurumax.com", "password": "admin"})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get Project ID (assuming first project)
    print("Fetching projects...")
    projects_res = session.get(f"{API_URL}/projects/projects", headers=headers)
    if projects_res.status_code != 200 or not projects_res.json():
        print("No projects found or failed to fetch.")
        return
    project_id = projects_res.json()[0]["id"]
    headers["X-Project-ID"] = project_id
    print(f"Using Project ID: {project_id}")

    # 2. Clear Data
    print("Clearing project data...")
    res = session.delete(CLEAR_URL, headers=headers)
    print(f"Clear response: {res.status_code} {res.text}")

    # 3. Verify Empty
    print("Verifying empty assets...")
    res = session.get(ASSETS_URL, headers=headers)
    assets = res.json()
    print(f"Assets count: {len(assets)}")
    if len(assets) != 0:
        print("❌ Data not cleared!")
    else:
        print("✅ Data cleared.")

    # 4. Import Dev CSV
    print("Importing Dev CSV...")
    res = session.post(IMPORT_URL, headers=headers)
    print(f"Import response: {res.status_code} {res.json()}")

    # 5. Verify Import
    print("Verifying imported assets...")
    res = session.get(ASSETS_URL, headers=headers)
    assets = res.json()
    print(f"Assets count: {len(assets)}")
    if len(assets) == 4:
        print("✅ Import successful (4 assets found).")
    else:
        print(f"❌ Import failed (found {len(assets)} assets).")

if __name__ == "__main__":
    verify()
