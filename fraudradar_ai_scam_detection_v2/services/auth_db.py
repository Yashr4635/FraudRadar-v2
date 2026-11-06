import os
import sqlite3
import hashlib
import secrets
import hmac
import datetime
import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger("fraudradar.auth_db")

DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "auth.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    """Initialize SQLite database with users, otps, and delivery logs."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    full_name TEXT NOT NULL,
                    password_hash TEXT,
                    is_verified INTEGER DEFAULT 0,
                    provider TEXT DEFAULT 'email',
                    created_at TEXT NOT NULL,
                    last_login_at TEXT
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS otps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL COLLATE NOCASE,
                    purpose TEXT NOT NULL,
                    otp_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 5,
                    consumed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_signups (
                    email TEXT PRIMARY KEY COLLATE NOCASE,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS delivery_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    status TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    error_message TEXT
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_otps_lookup ON otps(email, purpose, consumed);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON delivery_logs(timestamp);"
            )
    finally:
        conn.close()


# Initialize tables on module import
init_db()


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with 100,000 iterations and salt."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored salt$hash."""
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, expected = stored_hash.split("$", 1)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return hmac.compare_digest(dk.hex(), expected)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetch user by email address."""
    clean_email = (email or "").strip().lower()
    if not clean_email:
        return None
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ? LIMIT 1;", (clean_email,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user by ID."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ? LIMIT 1;", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_user(
    email: str,
    full_name: str,
    password: Optional[str] = None,
    is_verified: bool = False,
    provider: str = "email",
) -> Dict[str, Any]:
    """Create a new user record."""
    clean_email = email.strip().lower()
    user_id = secrets.token_hex(16)
    pw_hash = hash_password(password) if password else None
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO users (id, email, full_name, password_hash, is_verified, provider, created_at, last_login_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    full_name = excluded.full_name,
                    password_hash = COALESCE(excluded.password_hash, users.password_hash),
                    is_verified = excluded.is_verified,
                    provider = excluded.provider,
                    last_login_at = excluded.last_login_at;
                """,
                (
                    user_id,
                    clean_email,
                    full_name.strip() or clean_email.split("@")[0].title(),
                    pw_hash,
                    1 if is_verified else 0,
                    provider,
                    now,
                    now if is_verified else None,
                ),
            )
        return {
            "id": user_id,
            "email": clean_email,
            "full_name": full_name,
            "is_verified": is_verified,
            "provider": provider,
            "created_at": now,
        }
    finally:
        conn.close()


def store_pending_signup(email: str, full_name: str, password: str) -> None:
    """Store unverified signup credentials until OTP confirmation."""
    clean_email = email.strip().lower()
    pw_hash = hash_password(password)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO pending_signups (email, full_name, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    full_name = excluded.full_name,
                    password_hash = excluded.password_hash,
                    created_at = excluded.created_at;
                """,
                (clean_email, full_name.strip(), pw_hash, now),
            )
    finally:
        conn.close()


def commit_pending_signup(email: str) -> Optional[Dict[str, Any]]:
    """Commit verified signup from pending to active users."""
    clean_email = email.strip().lower()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM pending_signups WHERE email = ? LIMIT 1;", (clean_email,)
        )
        pending = cur.fetchone()
        if not pending:
            # Fallback if pending record was missing
            existing = get_user_by_email(clean_email)
            if existing:
                mark_user_verified(clean_email)
                return existing
            return create_user(
                clean_email,
                clean_email.split("@")[0].title(),
                is_verified=True,
            )

        user_id = secrets.token_hex(16)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with conn:
            conn.execute(
                """
                INSERT INTO users (id, email, full_name, password_hash, is_verified, provider, created_at, last_login_at)
                VALUES (?, ?, ?, ?, 1, 'email', ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    full_name = excluded.full_name,
                    password_hash = excluded.password_hash,
                    is_verified = 1,
                    last_login_at = excluded.last_login_at;
                """,
                (
                    user_id,
                    clean_email,
                    pending["full_name"],
                    pending["password_hash"],
                    now,
                    now,
                ),
            )
            conn.execute(
                "DELETE FROM pending_signups WHERE email = ?;", (clean_email,)
            )

        cur.execute("SELECT * FROM users WHERE email = ? LIMIT 1;", (clean_email,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def mark_user_verified(email: str) -> None:
    """Mark an existing user as verified and update last_login_at."""
    clean_email = email.strip().lower()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET is_verified = 1, last_login_at = ?
                WHERE email = ?;
                """,
                (now, clean_email),
            )
    finally:
        conn.close()


def update_last_login(email: str) -> None:
    """Update last login timestamp."""
    clean_email = email.strip().lower()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE users SET last_login_at = ? WHERE email = ?;",
                (now, clean_email),
            )
    finally:
        conn.close()


# ─── OTP Operations ─────────────────────────────────────────────────────────


def store_otp(
    email: str,
    purpose: str,
    otp: str,
    expires_in_seconds: int = 600,
    max_attempts: int = 5,
) -> None:
    """
    Store securely hashed OTP with cryptographic salt.
    Invalidates any prior active OTPs for the same (email, purpose).
    """
    clean_email = email.strip().lower()
    salt = secrets.token_hex(16)
    otp_hash = hashlib.sha256(f"{salt}:{otp}".encode("utf-8")).hexdigest()

    now_dt = datetime.datetime.now(datetime.timezone.utc)
    expires_dt = now_dt + datetime.timedelta(seconds=expires_in_seconds)

    conn = get_connection()
    try:
        with conn:
            # 1. Invalidate previous active OTPs for this email and purpose
            conn.execute(
                """
                UPDATE otps
                SET consumed = 1
                WHERE email = ? AND purpose = ? AND consumed = 0;
                """,
                (clean_email, purpose),
            )
            # 2. Insert new hashed OTP record
            conn.execute(
                """
                INSERT INTO otps (email, purpose, otp_hash, salt, expires_at, attempts, max_attempts, consumed, created_at)
                VALUES (?, ?, ?, ?, ?, 0, ?, 0, ?);
                """,
                (
                    clean_email,
                    purpose,
                    otp_hash,
                    salt,
                    expires_dt.isoformat(),
                    max_attempts,
                    now_dt.isoformat(),
                ),
            )
    finally:
        conn.close()


def verify_and_consume_otp(
    email: str, purpose: str, entered_code: str
) -> Tuple[bool, str]:
    """
    Verify OTP with constant-time comparison, single-use consumption,
    expiration check, and maximum failed attempt locking.
    """
    clean_email = email.strip().lower()
    clean_code = "".join(filter(str.isdigit, entered_code or "")).strip()

    if len(clean_code) != 8:
        return False, "Verification code must be exactly 8 digits."

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM otps
            WHERE email = ? AND purpose = ? AND consumed = 0
            ORDER BY id DESC LIMIT 1;
            """,
            (clean_email, purpose),
        )
        row = cur.fetchone()
        if not row:
            return False, "No active verification code found. Please request a new code."

        otp_id = row["id"]
        salt = row["salt"]
        expected_hash = row["otp_hash"]
        expires_at_str = row["expires_at"]
        attempts = row["attempts"]
        max_attempts = row["max_attempts"]

        now_dt = datetime.datetime.now(datetime.timezone.utc)
        expires_dt = datetime.datetime.fromisoformat(expires_at_str)

        # Check expiration
        if now_dt > expires_dt:
            with conn:
                conn.execute(
                    "UPDATE otps SET consumed = 1 WHERE id = ?;", (otp_id,)
                )
            return (
                False,
                "Verification code has expired. Please request a new code.",
            )

        # Check attempts lockout
        if attempts >= max_attempts:
            with conn:
                conn.execute(
                    "UPDATE otps SET consumed = 1 WHERE id = ?;", (otp_id,)
                )
            return (
                False,
                "Too many failed attempts. This code is invalidated. Please request a new code.",
            )

        # Constant-time cryptographic comparison
        computed_hash = hashlib.sha256(
            f"{salt}:{clean_code}".encode("utf-8")
        ).hexdigest()

        if hmac.compare_digest(computed_hash, expected_hash):
            with conn:
                conn.execute(
                    "UPDATE otps SET consumed = 1 WHERE id = ?;", (otp_id,)
                )
            return True, "Verification successful."

        # Increment attempts on failure
        new_attempts = attempts + 1
        with conn:
            if new_attempts >= max_attempts:
                conn.execute(
                    "UPDATE otps SET attempts = ?, consumed = 1 WHERE id = ?;",
                    (new_attempts, otp_id),
                )
                return (
                    False,
                    "Invalid verification code. Maximum attempts exceeded. Please request a new code.",
                )
            else:
                conn.execute(
                    "UPDATE otps SET attempts = ? WHERE id = ?;",
                    (new_attempts, otp_id),
                )
                remaining = max_attempts - new_attempts
                return (
                    False,
                    f"Invalid verification code. {remaining} attempt(s) remaining.",
                )
    finally:
        conn.close()


def check_rate_limit(
    email: str,
    purpose: str,
    window_seconds: int = 900,
    max_requests: int = 5,
) -> Tuple[bool, str]:
    """
    Check if email has exceeded maximum OTP issuance rate limit
    (e.g., max 5 requests per 15 minutes).
    """
    clean_email = email.strip().lower()
    now_dt = datetime.datetime.now(datetime.timezone.utc)
    window_start = (
        now_dt - datetime.timedelta(seconds=window_seconds)
    ).isoformat()

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) AS cnt FROM otps
            WHERE email = ? AND purpose = ? AND created_at >= ?;
            """,
            (clean_email, purpose, window_start),
        )
        count = cur.fetchone()["cnt"]
        if count >= max_requests:
            return (
                False,
                "Too many verification requests. Please wait 15 minutes before requesting again.",
            )
        return True, ""
    finally:
        conn.close()


# ─── Delivery Logging ────────────────────────────────────────────────────────


def log_delivery(
    recipient: str,
    purpose: str,
    status: str,
    provider: str,
    error_message: str = "",
) -> None:
    """Record an audit trail of email delivery attempts."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO delivery_logs (timestamp, recipient, purpose, status, provider, error_message)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    now,
                    recipient,
                    purpose,
                    status,
                    provider,
                    error_message or "",
                ),
            )
    finally:
        conn.close()


def get_delivery_logs(limit: int = 20) -> list:
    """Fetch recent email delivery audit logs."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM delivery_logs ORDER BY id DESC LIMIT ?;", (limit,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
