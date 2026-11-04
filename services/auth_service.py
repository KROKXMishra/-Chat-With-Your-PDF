import sqlite3
import bcrypt

from database.repository import (
    create_user,
    get_user_by_email
)


# Register a new user
def register_user(name, email, password):

    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "All fields are required."

    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    # bcrypt supports a maximum of 72 password bytes
    if len(password.encode("utf-8")) > 72:
        return False, "Password must not exceed 72 bytes."

    existing_user = get_user_by_email(email)

    if existing_user:
        return False, "An account with this email already exists."

    try:

        # Generate password hash
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Store user in database
        create_user(
            name,
            email,
            password_hash
        )

        return True, "Account created successfully!"

    except sqlite3.IntegrityError:

        return False, "This email is already registered."

    except Exception:

        return False, "Unable to create account. Please try again."


# Authenticate existing user
def authenticate_user(email, password):

    email = email.strip().lower()

    if not email or not password:
        return False, None

    user = get_user_by_email(email)

    if not user:
        return False, None

    stored_hash = user["password"]

    try:

        # Verify password against stored hash
        valid_password = bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )

    except (ValueError, TypeError):

        return False, None

    if not valid_password:
        return False, None

    # Return only required user information
    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }

    return True, user_data