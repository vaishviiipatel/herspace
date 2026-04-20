from datetime import datetime
from typing import Optional, List, Dict, Any


class User:
    def __init__(self, id: int, username: str, password: str, role: str = 'user'):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.created_at = datetime.now()

    def is_admin(self) -> bool:
        return self.role == 'admin'

    def is_moderator(self) -> bool:
        return self.role in ['moderator', 'admin']

    def can_delete_post(self, post_user_id: int) -> bool:
        return self.id == post_user_id or self.is_moderator()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }


class Post:
    def __init__(
        self,
        id: int,
        content: str,
        category: str,
        user_id: int,
        is_anonymous: bool = False,
        is_flagged: bool = False,
        is_approved: bool = True,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.content = content
        self.category = category
        self.user_id = user_id
        self.is_anonymous = is_anonymous
        self.is_flagged = is_flagged
        self.is_approved = is_approved
        self.created_at = created_at or datetime.now()

    def is_visible(self) -> bool:
        return self.is_approved and not self.is_flagged

    def needs_review(self) -> bool:
        return self.is_flagged or not self.is_approved

    def get_category_class(self) -> str:
        category_map = {
            'support': 'tag-support',
            'advice': 'tag-advice',
            'experience': 'tag-experience',
            'question': 'tag-question',
            'general': 'tag-general'
        }
        return category_map.get(self.category, 'tag-general')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content': self.content,
            'category': self.category,
            'user_id': self.user_id,
            'is_anonymous': self.is_anonymous,
            'is_flagged': self.is_flagged,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Comment:
    def __init__(
        self,
        id: int,
        content: str,
        user_id: int,
        post_id: int,
        is_anonymous: bool = False,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.content = content
        self.user_id = user_id
        self.post_id = post_id
        self.is_anonymous = is_anonymous
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content': self.content,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'is_anonymous': self.is_anonymous,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Like:
    def __init__(self, user_id: int, post_id: int, created_at: Optional[datetime] = None):
        self.user_id = user_id
        self.post_id = post_id
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Category:
    SUPPORT = 'support'
    ADVICE = 'advice'
    EXPERIENCE = 'experience'
    QUESTION = 'question'
    GENERAL = 'general'

    ALL = [SUPPORT, ADVICE, EXPERIENCE, QUESTION, GENERAL]

    @classmethod
    def get_display_name(cls, category: str) -> str:
        names = {
            cls.SUPPORT: 'Support',
            cls.ADVICE: 'Advice',
            cls.EXPERIENCE: 'Experience',
            cls.QUESTION: 'Question',
            cls.GENERAL: 'General'
        }
        return names.get(category, category.capitalize())

    @classmethod
    def is_valid(cls, category: str) -> bool:
        return category in cls.ALL


class Role:
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ALL = [USER, MODERATOR, ADMIN]

    @classmethod
    def can_moderate(cls, role: str) -> bool:
        return role in [cls.MODERATOR, cls.ADMIN]

    @classmethod
    def can_admin(cls, role: str) -> bool:
        return role == cls.ADMIN