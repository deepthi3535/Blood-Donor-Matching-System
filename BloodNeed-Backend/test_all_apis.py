"""Complete 8-step API test checklist."""
import json
import urllib.request
import urllib.error
import sys

BASE = "http://localhost:5000/api"
results = []


def call(method, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def check(name, ok, msg=""):
    status = "PASS" if ok else "FAIL"
    results.append((name, ok, msg))
    print(f"[{status}] {name}: {msg}")


print("=" * 60)
print("COMPLETE API TEST CHECKLIST")
print("=" * 60)

# Step 1: Patient register/login
code, res = call("POST", "/auth/login", {"email": "patient@example.com", "password": "Test@123"})
if not res.get("success"):
    code, res = call("POST", "/auth/register/patient", {
        "name": "Test Patient", "email": "patient@example.com", "phone": "9876543212",
        "password": "Test@123", "blood_group": "A+", "hospital_name": "City Hospital"
    })
patient_token = res.get("data", {}).get("token")
patient_id = res.get("data", {}).get("user", {}).get("patient_id")
check("4 Register Patient", res.get("success"), f"patient_id={patient_id}")

# Step 2: Create blood request
code, res = call("POST", "/request/blood", {
    "blood_group": "O+", "units_needed": 2, "emergency_level": "Critical",
    "hospital_name": "Apollo Hospital", "hospital_latitude": 19.0860,
    "hospital_longitude": 72.8857, "notes": "Patient needs urgent blood transfusion"
}, patient_token)
request_id = res.get("data", {}).get("request_id")
check("5 Create Blood Request", res.get("success"), f"request_id={request_id}")

# Step 3: Get patient requests
code, res = call("GET", "/request/patient/requests", token=patient_token)
check("6 Get Patient Requests", res.get("success") and len(res.get("data", [])) > 0,
      f"count={len(res.get('data', []))}")

# Ensure O+ donor available
code, res = call("POST", "/auth/login", {"email": "donor3@example.com", "password": "Test@123"})
if not res.get("success"):
    code, res = call("POST", "/auth/register/donor", {
        "name": "Test Donor", "email": "donor3@example.com", "phone": "9876543213",
        "password": "Test@123", "blood_group": "O+"
    })
donor_token = res.get("data", {}).get("token")
call("POST", "/donor/availability", {"available": True}, donor_token)

# Step 4: Find matching donors
code, res = call("GET", f"/matching/find/{request_id}", token=patient_token)
check("7 Find Matching Donors", res.get("success"),
      f"total_donors={res.get('data', {}).get('total_donors', 0)}")

# Step 5: Get donor ranking
code, res = call("GET", f"/matching/ranking/{request_id}", token=patient_token)
check("8 Get Donor Ranking", res.get("success"), f"matches={len(res.get('data', []))}")

# Step 6: Donor history
code, res = call("GET", "/donor/history", token=donor_token)
check("9 Get Donor History", res.get("success"), f"items={len(res.get('data', []))}")

# Step 7: Update availability
code, res = call("POST", "/donor/availability", {"available": False}, donor_token)
check("10 Update Availability", res.get("success"), res.get("message", ""))

# Step 8: Gamification
code, res = call("GET", "/donor/gamification", token=donor_token)
check("11 Get Gamification", res.get("success"), f"tier={res.get('data', {}).get('tier')}")

print("=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULTS: {passed}/{len(results)} passed")
print("=" * 60)
sys.exit(0 if passed == len(results) else 1)
