"""
Firebase utilities for the Autonomous Strategy Evolution Platform.
Handles all Firestore interactions with proper error handling and connection management.
"""

import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json
from dataclasses import asdict

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Manages Firebase connection and provides CRUD operations"""
    
    _instance = None
    _db = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def initialize(self, cred_path: Optional[str] = None) -> None:
        """Initialize Firebase connection with proper error handling"""
        if self._initialized:
            logger.info("Firebase already initialized")
            return
            
        try:
            if cred_path:
                cred = credentials.Certificate(cred_path)
            elif firebase_admin._apps:
                # Already initialized elsewhere
                self._db = firestore.client()
                self._initialized = True
                return
            else:
                # Use default credentials (for Google Cloud environments)
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred)
            self._db = firestore.client()
            self._initialized = True
            logger.info("Firebase initialized successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Firebase credentials file not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid Firebase credentials: {e}")
            raise
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase initialization error: {e}")
            raise
    
    @property
    def db(self) -> firestore.Client:
        """Get Firestore client with lazy initialization"""
        if not self._initialized:
            self.initialize()
        if self._db is None:
            raise RuntimeError("Firestore client not available")
        return self._db
    
    def save_strategy(self, strategy_data: Dict[str, Any], collection: str = "strategies") -> str:
        """Save a strategy to Firestore with timestamp"""
        try:
            # Add metadata
            strategy_data['created_at'] = firestore.SERVER_TIMESTAMP
            strategy_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection(collection).document()
            doc_ref.set(strategy_data)
            
            logger.info(f"Strategy saved with ID: {doc_ref.id}")
            return doc_ref.id
            
        except exceptions.FirebaseError as e:
            logger.error(f"Failed to save strategy: {e}")
            raise
    
    def get_strategies(self, 
                      collection: str = "strategies",
                      filters: Optional[Dict[str, Any]] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve strategies with optional filters"""
        try:
            query = self.db.collection(collection)
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    query = query.where(field, "==", value)
            
            # Apply limit
            query = query.limit(limit)
            
            results = []
            for doc in query.stream():