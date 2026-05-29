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

# Test officer registration data (officer role = pending approval)
test_officer = {
    "username": "testofficer",
    "email": "testofficer@example.com",
    "password": "test123",
    "full_name": "Test Officer",
    "role": "officer",
    "barangay": "Sample Barangay",
    "contact_number": "09123456789"
}

test_admin = {
    "username": "testadmin",
    "email": "testadmin@example.com",
    "password": "test123",
    "full_name": "Test Admin",
    "role": "admin",
    "barangay": "Sample Barangay",
    "contact_number": "09123456789",
    "admin_secret": "test-admin-secret"
}

admin_login_data = {
    "username": "testadmin",
    "password": "test123"
}

officer_login_data = {
    "username": "testofficer",
    "password": "test123"
}

token = None
admin_token = None
officer_user_id = None


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

    res = requests.post(f"{BASE_URL}/submit_report", data=report_data)
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
# 7. REGISTER OFFICER (pending approval)
# =========================
def test_register_officer():
    print("\n[TEST] Register Officer (should be pending)")
    res = requests.post(f"{BASE_URL}/api/register", json=test_officer)
    print(res.status_code, res.json())


# =========================
# 8. OFFICER LOGIN (should fail - pending)
# =========================
def test_officer_login_pending():
    print("\n[TEST] Officer Login while PENDING (should fail)")
    res = requests.post(f"{BASE_URL}/api/login", json=officer_login_data)
    print(res.status_code, res.json())


# =========================
# 9. REGISTER ADMIN
# =========================
def test_register_admin():
    print("\n[TEST] Register Admin")
    res = requests.post(f"{BASE_URL}/api/register", json=test_admin)
    print(res.status_code, res.json())


# =========================
# 10. ADMIN LOGIN
# =========================
def test_admin_login():
    global admin_token
    print("\n[TEST] Admin Login")
    res = requests.post(f"{BASE_URL}/api/login", json=admin_login_data)
    print(res.status_code, res.json())
    if res.status_code == 200:
        admin_token = res.json().get("access_token")


# =========================
# 11. ADMIN APPROVES OFFICER
# =========================
def test_approve_officer():
    global officer_user_id
    print("\n[TEST] Admin Approve Officer")
    # Find the officer user
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = requests.get(f"{BASE_URL}/api/users", headers=headers)
    users = res.json()
    officer = next((u for u in users if u["username"] == "testofficer"), None)
    if officer:
        officer_user_id = officer["id"]
        res2 = requests.post(f"{BASE_URL}/api/users/{officer['id']}/approve", headers=headers)
        print(res2.status_code, res2.json())
    else:
        print("Officer not found in users list")


# =========================
# 12. OFFICER LOGIN (should succeed now)
# =========================
def test_officer_login_approved():
    print("\n[TEST] Officer Login after APPROVAL (should succeed)")
    res = requests.post(f"{BASE_URL}/api/login", json=officer_login_data)
    print(res.status_code, res.json())


# =========================
# 13. ADMIN REJECTS A DIFFERENT TEST OFFICER
# =========================
def test_reject_officer():
    print("\n[TEST] Admin Reject Officer")
    if officer_user_id:
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = requests.post(f"{BASE_URL}/api/users/{officer_user_id}/reject", headers=headers)
        print(res.status_code, res.json())


# =========================
# 14. OFFICER LOGIN (should fail - rejected)
# =========================
def test_officer_login_rejected():
    print("\n[TEST] Officer Login after REJECTION (should fail)")
    res = requests.post(f"{BASE_URL}/api/login", json=officer_login_data)
    print(res.status_code, res.json())


# =========================
# 15. ADMIN APPROVES OFFICER AGAIN FOR ARCHIVE TEST
# =========================
def test_approve_officer_again():
    print("\n[TEST] Admin Approve Officer again (for archive test)")
    if officer_user_id:
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = requests.post(f"{BASE_URL}/api/users/{officer_user_id}/approve", headers=headers)
        print(res.status_code, res.json())


# =========================
# 16. ADMIN ARCHIVES OFFICER
# =========================
def test_archive_officer():
    print("\n[TEST] Admin Archive Officer")
    if officer_user_id:
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = requests.post(f"{BASE_URL}/api/users/{officer_user_id}/archive", headers=headers)
        print(res.status_code, res.json())


# =========================
# 17. OFFICER LOGIN (should fail - archived)
# =========================
def test_officer_login_archived():
    print("\n[TEST] Officer Login after ARCHIVE (should fail)")
    res = requests.post(f"{BASE_URL}/api/login", json=officer_login_data)
    print(res.status_code, res.json())


# =========================
# 18. ADMIN DELETES OFFICER
# =========================
def test_delete_officer():
    print("\n[TEST] Admin Delete Officer")
    if officer_user_id:
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = requests.delete(f"{BASE_URL}/api/users/{officer_user_id}/delete", headers=headers)
        print(res.status_code, res.json())


# =========================
# 19. VERIFY OFFICER DELETED
# =========================
def test_officer_deleted():
    print("\n[TEST] Verify Officer Deleted")
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = requests.get(f"{BASE_URL}/api/users", headers=headers)
    users = res.json()
    found = any(u["username"] == "testofficer" for u in users)
    print(f"Officer found in list: {found}")


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
    test_register_officer()
    test_officer_login_pending()
    test_register_admin()
    test_admin_login()
    test_approve_officer()
    test_officer_login_approved()
    test_reject_officer()
    test_officer_login_rejected()
    test_approve_officer_again()
    test_archive_officer()
    test_officer_login_archived()
    test_delete_officer()
    test_officer_deleted()

    print("\nALL TESTS COMPLETED")