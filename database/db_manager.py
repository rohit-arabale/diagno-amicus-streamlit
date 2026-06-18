import hashlib
import json
import os
from datetime import datetime

db = None
SERVER_TIMESTAMP = None
if os.getenv("DIAGNO_USE_FIREBASE", "0").lower() in ("1", "true", "yes"):
    try:
        from google.cloud.firestore import SERVER_TIMESTAMP
        from firebase_setup import db
    except Exception:
        db = None

ROOT = os.path.dirname(os.path.abspath(__file__))
LOCAL_STORE_PATH = os.path.join(ROOT, "local_store.json")


def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def _load_store() -> dict:
    if not os.path.exists(LOCAL_STORE_PATH):
        return {"users": [], "predictions": [], "next_user_id": 1, "next_prediction_id": 1}
    try:
        with open(LOCAL_STORE_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    data.setdefault("users", [])
    data.setdefault("predictions", [])
    data.setdefault("next_user_id", 1)
    data.setdefault("next_prediction_id", 1)
    return data


def _save_store(data: dict) -> None:
    with open(LOCAL_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def create_user(name: str, mobile: str, age: int, gender: str, password: str) -> dict:
    """
    Register a new user. Firestore is used when it responds; otherwise the
    bundled JSON store keeps the project usable without cloud setup.
    """
    if db is not None:
        try:
            users_ref = db.collection("users")
            query = users_ref.where("name", "==", name.strip()).limit(1).get()
            if len(query) > 0:
                return {"ok": False, "error": "A user with that name already exists."}

            users_ref.add(
                {
                    "name": name.strip(),
                    "mobile": mobile.strip(),
                    "age": age,
                    "gender": gender,
                    "password": hash_password(password),
                    "created_at": SERVER_TIMESTAMP,
                }
            )
            return {"ok": True}
        except Exception:
            pass

    try:
        store = _load_store()
        if any(user["name"].strip().lower() == name.strip().lower() for user in store["users"]):
            return {"ok": False, "error": "A user with that name already exists."}
        user_id = store["next_user_id"]
        store["next_user_id"] += 1
        store["users"].append(
            {
                "id": user_id,
                "name": name.strip(),
                "mobile": mobile.strip(),
                "age": age,
                "gender": gender,
                "password": hash_password(password),
            }
        )
        _save_store(store)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def login_user(name: str, age: int, password: str) -> dict:
    """
    Validate login credentials against Firestore first, then local JSON.
    """
    if db is not None:
        try:
            users_ref = db.collection("users")
            query = users_ref.where("name", "==", name.strip()).where("age", "==", age).limit(1).get()
            if len(query) > 0:
                doc = query[0]
                user_data = doc.to_dict()
                if not verify_password(password, user_data["password"]):
                    return {"ok": False, "error": "Incorrect password."}
                return {
                    "ok": True,
                    "user": {
                        "id": str(doc.id),
                        "name": user_data["name"],
                        "mobile": user_data["mobile"],
                        "age": user_data["age"],
                        "gender": user_data["gender"],
                    },
                }
        except Exception:
            pass

    try:
        store = _load_store()
        user = next(
            (
                item
                for item in store["users"]
                if item["name"].strip().lower() == name.strip().lower() and int(item["age"]) == age
            ),
            None,
        )
        if user is None:
            return {"ok": False, "error": "No account found with that name and age."}
        if not verify_password(password, user["password"]):
            return {"ok": False, "error": "Incorrect password."}
        return {
            "ok": True,
            "user": {
                "id": f"local:{user['id']}",
                "name": user["name"],
                "mobile": user["mobile"],
                "age": user["age"],
                "gender": user["gender"],
            },
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def save_prediction(
    user_id: str,
    patient_data: dict,
    results: dict,
    top_disease: str,
    top_probability: float,
) -> None:
    if db is not None and not str(user_id).startswith("local:"):
        try:
            db.collection("predictions").add(
                {
                    "user_id": user_id,
                    "timestamp": SERVER_TIMESTAMP,
                    "input_data": patient_data,
                    "results": results,
                    "top_disease": top_disease,
                    "top_probability": top_probability,
                }
            )
            return
        except Exception:
            pass

    store = _load_store()
    prediction_id = store["next_prediction_id"]
    store["next_prediction_id"] += 1
    store["predictions"].append(
        {
            "id": prediction_id,
            "user_id": str(user_id),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "input_data": patient_data,
            "results": results,
            "top_disease": top_disease,
            "top_probability": float(top_probability),
        }
    )
    _save_store(store)


def list_predictions(user_id: str, limit: int | None = None) -> list[dict]:
    if db is not None and not str(user_id).startswith("local:"):
        try:
            from firebase_admin import firestore

            query = (
                db.collection("predictions")
                .where("user_id", "==", user_id)
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
            )
            if limit:
                query = query.limit(limit)

            records = []
            for doc in query.stream():
                data = doc.to_dict()
                ts = data.get("timestamp")
                records.append(
                    {
                        "id": doc.id,
                        "timestamp": ts.strftime("%Y-%m-%d %H:%M") if ts else "Unknown",
                        "top_disease": data.get("top_disease", ""),
                        "top_probability": data.get("top_probability", 0),
                        "input_data": data.get("input_data", {}),
                        "results": data.get("results", {}),
                    }
                )
            return records
        except Exception:
            pass

    store = _load_store()
    records = [
        {
            "id": f"local:{item['id']}",
            "timestamp": item["timestamp"],
            "top_disease": item["top_disease"],
            "top_probability": item["top_probability"],
            "input_data": item.get("input_data", {}),
            "results": item.get("results", {}),
        }
        for item in store["predictions"]
        if item["user_id"] == str(user_id)
    ]
    records.sort(key=lambda item: item["timestamp"], reverse=True)
    return records[:limit] if limit else records
