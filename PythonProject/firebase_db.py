"""
Firebase Firestore Database
----------------------------
Replaces MongoDB with Firebase for consistency
"""
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

class FirebaseDB:
    """Firebase Firestore Manager"""
    db = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase (called from app startup)"""
        if not firebase_admin._apps:
            cred_path = Path(__file__).resolve().parent / "serviceAccountKey.json"
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
        
        cls.db = firestore.client()
        print("✅ Firebase Firestore connected")
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get Firestore collection"""
        return cls.db.collection(collection_name)

# Collection names
VALIDATIONS_COLLECTION = "startup_validations"
