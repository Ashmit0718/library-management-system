"""debug_login.py — diagnose why login returns 401"""
import os, sys
from dotenv import load_dotenv
load_dotenv()

# 1. Direct DB + bcrypt check
print("=" * 55)
print("STEP 1 — Checking password hashes directly in the DB")
print("=" * 55)

from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User

app = create_app()
with app.app_context():
    test_cases = [
        ("priya@library.com",         "Priya123"),
        ("ravi@library.com",          "Ravi123"),
        ("ananya@library.com",        "Ananya123"),
        ("24104139@apsit.edu.in",     "Admin@123"),
    ]
    for email, pw in test_cases:
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"  ✗  {email}  →  USER NOT FOUND IN DB")
            continue
        ok = bcrypt.check_password_hash(user.password_hash, pw)
        status = "✓ OK" if ok else "✗ HASH MISMATCH"
        print(f"  {status}  {email} / {pw}  (role={user.role}, active={user.is_active})")

# 2. Live HTTP test
print()
print("=" * 55)
print("STEP 2 — Live HTTP login test against running server")
print("=" * 55)
import urllib.request, json

for email, pw in [("priya@library.com","Priya123"), ("24104139@apsit.edu.in","Admin@123")]:
    body = json.dumps({"email": email, "password": pw}).encode()
    req  = urllib.request.Request(
        "http://127.0.0.1:5000/api/auth/login",
        data=body, method="POST",
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
            print(f"  ✓ {email}  →  200 OK  role={data['user']['role']}")
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"  ✗ {email}  →  {e.code}  error={err}")
    except Exception as e:
        print(f"  ✗ {email}  →  server error: {e}")
