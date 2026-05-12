import requests

BASE_URL = "http://127.0.0.1:8000"

# =========================
# TEST DATA
# =========================
test_user = {
    "username": "testvictim",
    "email": "testvictim@example.com",
    "password": "test123",
    "full_name": "Test Victim",
    "role": "victim",
    "barangay": "Sample Barangay",
    "contact_number": "09123456789"
}

login_data = {
    "username": "testvictim",
    "password": "test123"
}

report_data = {
    "victim_name": "Test Victim",
    "contact_number": "09123456789",
    "incident_type": "Harassment",
    "description": "Test case for API validation",
    "location": "Manila"
}

token = None


# =========================
# 1. REGISTER USER
# =========================
def test_register():
    print("\n[TEST] Register User")
    res = requests.post(f"{BASE_URL}/api/register", json=test_user)
    print(res.status_code, res.json())


# =========================
# 2. LOGIN USER
# =========================
def test_login():
    global token
    print("\n[TEST] Login User")

    res = requests.post(f"{BASE_URL}/api/login", json=login_data)
    print(res.status_code, res.json())

    if res.status_code == 200:
        token = res.json().get("access_token")


# =========================
# 3. GET USER INFO
# =========================
def test_get_me():
    print("\n[TEST] Get User Info")

    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/api/me", headers=headers)

    print(res.status_code, res.json())


# =========================
# 4. SUBMIT REPORT
# =========================
def test_submit_report():
    print("\n[TEST] Submit Report")

    res = requests.post(f"{BASE_URL}/submit_report", json=report_data)
    print(res.status_code, res.json())


# =========================
# 5. GET REPORTS
# =========================
def test_get_reports():
    print("\n[TEST] Get Reports")

    res = requests.get(f"{BASE_URL}/view_reports")
    print(res.status_code, res.json())


# =========================
# 6. DASHBOARD STATS
# =========================
def test_dashboard():
    print("\n[TEST] Dashboard Stats")

    res = requests.get(f"{BASE_URL}/api/dashboard/stats")
    print(res.status_code, res.json())


# =========================
# RUN ALL TESTS
# =========================
if __name__ == "__main__":
    test_register()
    test_login()
    test_get_me()
    test_submit_report()
    test_get_reports()
    test_dashboard()

    print("\nALL TESTS COMPLETED")