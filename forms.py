from typing import Dict, List, Optional, Tuple
import re


class ValidationError:
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

    def __str__(self):
        return f"{self.field}: {self.message}"

    def to_dict(self):
        return {'field': self.field, 'message': self.message}


class FormValidator:
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 30
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 50
    MIN_POST_LENGTH = 10
    MAX_POST_LENGTH = 2000
    MIN_COMMENT_LENGTH = 1
    MAX_COMMENT_LENGTH = 500

    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')
    VALID_CATEGORIES = ['support', 'advice', 'experience', 'question', 'general']

    @staticmethod
    def validate_username(username: str) -> List[ValidationError]:
        errors = []
        if not username:
            errors.append(ValidationError('username', 'Username is required.'))
            return errors
        if len(username) < FormValidator.MIN_USERNAME_LENGTH:
            errors.append(ValidationError(
                'username',
                f'Username must be at least {FormValidator.MIN_USERNAME_LENGTH} characters.'
            ))
        if len(username) > FormValidator.MAX_USERNAME_LENGTH:
            errors.append(ValidationError(
                'username',
                f'Username must be less than {FormValidator.MAX_USERNAME_LENGTH} characters.'
            ))
        if not FormValidator.USERNAME_PATTERN.match(username):
            errors.append(ValidationError(
                'username',
                'Username can only contain letters, numbers, and underscores.'
            ))
        return errors

    @staticmethod
    def validate_password(password: str) -> List[ValidationError]:
        errors = []
        if not password:
            errors.append(ValidationError('password', 'Password is required.'))
            return errors
        if len(password) < FormValidator.MIN_PASSWORD_LENGTH:
            errors.append(ValidationError(
                'password',
                f'Password must be at least {FormValidator.MIN_PASSWORD_LENGTH} characters.'
            ))
        if len(password) > FormValidator.MAX_PASSWORD_LENGTH:
            errors.append(ValidationError(
                'password',
                f'Password must be less than {FormValidator.MAX_PASSWORD_LENGTH} characters.'
            ))
        return errors

    @staticmethod
    def validate_passwords_match(password: str, confirm: str) -> List[ValidationError]:
        errors = []
        if password != confirm:
            errors.append(ValidationError('confirm_password', 'Passwords do not match.'))
        return errors

    @staticmethod
    def validate_post_content(content: str) -> List[ValidationError]:
        errors = []
        if not content or not content.strip():
            errors.append(ValidationError('content', 'Post content is required.'))
            return errors
        if len(content) < FormValidator.MIN_POST_LENGTH:
            errors.append(ValidationError(
                'content',
                f'Post must be at least {FormValidator.MIN_POST_LENGTH} characters.'
            ))
        if len(content) > FormValidator.MAX_POST_LENGTH:
            errors.append(ValidationError(
                'content',
                f'Post must be less than {FormValidator.MAX_POST_LENGTH} characters.'
            ))
        return errors

    @staticmethod
    def validate_category(category: str) -> List[ValidationError]:
        errors = []
        if not category:
            errors.append(ValidationError('category', 'Category is required.'))
            return errors
        if category not in FormValidator.VALID_CATEGORIES:
            errors.append(ValidationError('category', 'Invalid category selected.'))
        return errors

    @staticmethod
    def validate_comment(content: str) -> List[ValidationError]:
        errors = []
        if not content or not content.strip():
            errors.append(ValidationError('content', 'Comment is required.'))
            return errors
        if len(content) < FormValidator.MIN_COMMENT_LENGTH:
            errors.append(ValidationError(
                'content',
                f'Comment must be at least {FormValidator.MIN_COMMENT_LENGTH} character.'
            ))
        if len(content) > FormValidator.MAX_COMMENT_LENGTH:
            errors.append(ValidationError(
                'content',
                f'Comment must be less than {FormValidator.MAX_COMMENT_LENGTH} characters.'
            ))
        return errors


class LoginForm:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.errors: Dict[str, List[str]] = {}

    def validate(self) -> bool:
        self.errors = {}
        username_errors = FormValidator.validate_username(self.username)
        password_errors = FormValidator.validate_password(self.password)
        if username_errors:
            self.errors['username'] = [e.message for e in username_errors]
        if password_errors:
            self.errors['password'] = [e.message for e in password_errors]
        return len(self.errors) == 0

    def has_errors(self) -> bool:
        return len(self.errors) > 0


class RegisterForm:
    def __init__(self, username: str, password: str, confirm_password: str):
        self.username = username
        self.password = password
        self.confirm_password = confirm_password
        self.errors: Dict[str, List[str]] = {}

    def validate(self) -> bool:
        self.errors = {}
        username_errors = FormValidator.validate_username(self.username)
        password_errors = FormValidator.validate_password(self.password)
        match_errors = FormValidator.validate_passwords_match(
            self.password,
            self.confirm_password
        )
        if username_errors:
            self.errors['username'] = [e.message for e in username_errors]
        if password_errors:
            self.errors['password'] = [e.message for e in password_errors]
        if match_errors:
            self.errors['confirm_password'] = [e.message for e in match_errors]
        return len(self.errors) == 0

    def has_errors(self) -> bool:
        return len(self.errors) > 0


class PostForm:
    def __init__(self, content: str, category: str, is_anonymous: bool = False):
        self.content = content
        self.category = category
        self.is_anonymous = is_anonymous
        self.errors: Dict[str, List[str]] = {}

    def validate(self) -> bool:
        self.errors = {}
        content_errors = FormValidator.validate_post_content(self.content)
        category_errors = FormValidator.validate_category(self.category)
        if content_errors:
            self.errors['content'] = [e.message for e in content_errors]
        if category_errors:
            self.errors['category'] = [e.message for e in category_errors]
        return len(self.errors) == 0

    def has_errors(self) -> bool:
        return len(self.errors) > 0


class CommentForm:
    def __init__(self, content: str, is_anonymous: bool = False):
        self.content = content
        self.is_anonymous = is_anonymous
        self.errors: Dict[str, List[str]] = {}

    def validate(self) -> bool:
        self.errors = {}
        content_errors = FormValidator.validate_comment(self.content)
        if content_errors:
            self.errors['content'] = [e.message for e in content_errors]
        return len(self.errors) == 0

    def has_errors(self) -> bool:
        return len(self.errors) > 0


class RoleForm:
    @staticmethod
    def validate_role(role: str) -> Tuple[bool, Optional[str]]:
        valid_roles = ['user', 'moderator', 'admin']
        if role not in valid_roles:
            return False, 'Invalid role selected.'
        return True, None