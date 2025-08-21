"""
Database Service for AI Assistant Bot
Handles JSON file operations for user sessions and conversations
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from config import DATA_DIR, USER_DATA_FILE, CONVERSATION_DATA_FILE

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for managing user sessions and conversations."""
    
    def __init__(self):
        """Initialize database service."""
        self._ensure_data_directory()
        self.users_file = USER_DATA_FILE
        self.conversations_file = CONVERSATION_DATA_FILE
    
    def _ensure_data_directory(self):
        """Ensure data directory exists."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logger.info(f"Created data directory: {DATA_DIR}")
    
    def _load_users_data(self) -> Dict[str, Any]:
        """Load users data from JSON file."""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading users data: {e}")
            return {}
    
    def _save_users_data(self, data: Dict[str, Any]) -> bool:
        """Save users data to JSON file."""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except IOError as e:
            logger.error(f"Error saving users data: {e}")
            return False
    
    def _load_conversations_data(self) -> Dict[str, Any]:
        """Load conversations data from JSON file."""
        try:
            if os.path.exists(self.conversations_file):
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading conversations data: {e}")
            return {}
    
    def _save_conversations_data(self, data: Dict[str, Any]) -> bool:
        """Save conversations data to JSON file."""
        try:
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except IOError as e:
            logger.error(f"Error saving conversations data: {e}")
            return False
    
    def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user session data by user ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User session data or None if not found
        """
        try:
            users_data = self._load_users_data()
            user_id_str = str(user_id)
            
            if user_id_str in users_data:
                return users_data[user_id_str]
            else:
                # Create new user session
                new_session = self._create_default_user_session(user_id)
                users_data[user_id_str] = new_session
                self._save_users_data(users_data)
                return new_session
                
        except Exception as e:
            logger.error(f"Error getting user session: {e}")
            return None
    
    def update_user_session(self, user_id: int, data: Dict[str, Any]) -> bool:
        """
        Update user session data.
        
        Args:
            user_id: Telegram user ID
            data: Updated session data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            users_data = self._load_users_data()
            user_id_str = str(user_id)
            
            if user_id_str not in users_data:
                users_data[user_id_str] = self._create_default_user_session(user_id)
            
            # Update existing data
            users_data[user_id_str].update(data)
            users_data[user_id_str]['updated_at'] = datetime.now().isoformat()
            
            return self._save_users_data(users_data)
            
        except Exception as e:
            logger.error(f"Error updating user session: {e}")
            return False
    
    def update_user_field(self, user_id: int, field: str, value: Any) -> bool:
        """
        Update specific user field.
        
        Args:
            user_id: Telegram user ID
            field: Field name to update
            value: New field value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            users_data = self._load_users_data()
            user_id_str = str(user_id)
            
            if user_id_str not in users_data:
                users_data[user_id_str] = self._create_default_user_session(user_id)
            
            users_data[user_id_str][field] = value
            users_data[user_id_str]['updated_at'] = datetime.now().isoformat()
            
            return self._save_users_data(users_data)
            
        except Exception as e:
            logger.error(f"Error updating user field: {e}")
            return False
    
    def add_conversation_message(self, user_id: int, message: str, sender: str) -> bool:
        """
        Add a conversation message to the database.
        
        Args:
            user_id: Telegram user ID
            message: Message content
            sender: 'user' or 'bot'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conversations_data = self._load_conversations_data()
            user_id_str = str(user_id)
            
            if user_id_str not in conversations_data:
                conversations_data[user_id_str] = []
            
            message_data = {
                'message': message,
                'sender': sender,
                'timestamp': datetime.now().isoformat()
            }
            
            conversations_data[user_id_str].append(message_data)
            
            # Keep only last 50 messages per user
            if len(conversations_data[user_id_str]) > 50:
                conversations_data[user_id_str] = conversations_data[user_id_str][-50:]
            
            return self._save_conversations_data(conversations_data)
            
        except Exception as e:
            logger.error(f"Error adding conversation message: {e}")
            return False
    
    def get_conversation_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        try:
            conversations_data = self._load_conversations_data()
            user_id_str = str(user_id)
            
            if user_id_str in conversations_data:
                return conversations_data[user_id_str][-limit:]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def _create_default_user_session(self, user_id: int) -> Dict[str, Any]:
        """Create default user session."""
        return {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'language': 'auto',
            'survey_completed': False,
            'preferences': {},
            'in_survey_mode': False,
            'start_option_chosen': None
        }