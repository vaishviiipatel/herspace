from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import hashlib
import hmac
import secrets


def hash_password(password: str, salt: Optional[str] = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, hash_hex = hashed.split('$')
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return hmac.compare_digest(new_hash.hex(), hash_hex)
    except ValueError:
        return False


def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def sanitize_html(text: str) -> str:
    html_escape_table = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)


def format_datetime(dt: datetime, format: str = 'relative') -> str:
    if format == 'relative':
        return format_relative_time(dt)
    elif format == 'short':
        return dt.strftime('%b %d, %Y')
    elif format == 'time':
        return dt.strftime('%I:%M %p')
    else:
        return dt.strftime('%b %d, %Y at %I:%M %p')


def format_relative_time(dt: datetime) -> str:
    now = datetime.now()
    diff = now - dt
    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif diff < timedelta(days=7):
        days = diff.days
        return f'{days} day{"s" if days != 1 else ""} ago'
    elif diff < timedelta(days=30):
        weeks = int(diff.days / 7)
        return f'{weeks} week{"s" if weeks != 1 else ""} ago'
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return f'{months} month{"s" if months != 1 else ""} ago'
    else:
        years = int(diff.days / 365)
        return f'{years} year{"s" if years != 1 else ""} ago'


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    if count == 1:
        return f"{count} {singular}"
    if plural is None:
        plural = singular + 's'
    return f"{count} {plural}"


def get_client_ip(request) -> str:
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    return request.environ.get('REMOTE_ADDR', '0.0.0.0')


def calculate_pagination(
    current_page: int,
    total_items: int,
    items_per_page: int
) -> Dict[str, Any]:
    total_pages = (total_items + items_per_page - 1) // items_per_page
    return {
        'current_page': current_page,
        'total_pages': total_pages,
        'total_items': total_items,
        'items_per_page': items_per_page,
        'has_prev': current_page > 1,
        'has_next': current_page < total_pages,
        'offset': (current_page - 1) * items_per_page
    }


def paginate_list(
    items: List[Any],
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = items[start:end]
    pagination = calculate_pagination(page, total, per_page)
    return {
        'items': paginated,
        'pagination': pagination
    }


def generate_slug(text: str) -> str:
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


CATEGORY_COLORS = {
    'support': '#f5d0e0',
    'advice': '#e8d8f5',
    'experience': '#d8eedc',
    'question': '#fdecd0',
    'general': '#e0ecf8'
}


ROLE_COLORS = {
    'admin': '#d4527a',
    'moderator': '#9e60c8',
    'user': '#d8eedc'
}


def get_category_color(category: str) -> str:
    return CATEGORY_COLORS.get(category, '#e0ecf8')


def get_role_color(role: str) -> str:
    return ROLE_COLORS.get(role, '#d8eedc')


def calculate_read_time(text: str, words_per_minute: int = 200) -> int:
    words = len(text.split())
    minutes = max(1, words // words_per_minute)
    return minutes


def extract_mentions(text: str) -> List[str]:
    import re
    pattern = r'@(\w+)'
    return re.findall(pattern, text)


def extract_hashtags(text: str) -> List[str]:
    import re
    pattern = r'#(\w+)'
    return re.findall(pattern, text)


class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[datetime]] = {}

    def is_allowed(self, identifier: str) -> bool:
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)
        if identifier not in self.requests:
            self.requests[identifier] = []
        self.requests[identifier] = [
            req for req in self.requests[identifier]
            if req > cutoff
        ]
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        self.requests[identifier].append(now)
        return True

    def get_remaining(self, identifier: str) -> int:
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)
        if identifier not in self.requests:
            return self.max_requests
        recent = [
            req for req in self.requests[identifier]
            if req > cutoff
        ]
        return max(0, self.max_requests - len(recent))

    def reset(self, identifier: str) -> None:
        if identifier in self.requests:
            del self.requests[identifier]


class Cache:
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        entry = self.cache[key]
        if datetime.now() > entry['expires']:
            del self.cache[key]
            return None
        return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=ttl)
        }

    def delete(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]

    def clear(self) -> None:
        self.cache.clear()

    def cleanup(self) -> None:
        now = datetime.now()
        expired = [
            key for key, entry in self.cache.items()
            if now > entry['expires']
        ]
        for key in expired:
            del self.cache[key]