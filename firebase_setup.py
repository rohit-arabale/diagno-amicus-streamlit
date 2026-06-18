import json
import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

load_dotenv()

ROOT = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(ROOT, "serviceAccountKey.json")

if os.getenv("FIREBASE_SERVICE_ACCOUNT"):
    cred_dict = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
    cred = credentials.Certificate(cred_dict)
else:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
