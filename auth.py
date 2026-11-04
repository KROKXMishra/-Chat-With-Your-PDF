
import bcrypt

from database import (
    create_user,
    get_user_by_email
)


# -------------------- REGISTER --------------------

def register_user(name, email, password):

    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "All fields are required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    # Check whether email already exists
    existing_user = get_user_by_email(email)

    if existing_user:
        return False, "An account with this email already exists."

    # Hash password
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:

        create_user(
            name,
            email,
            password_hash
        )

        return True, "Account created successfully!"

    except Exception:
        return False, "Unable to create account. Please try again."


# -------------------- LOGIN --------------------

def login_user(email, password):

    email = email.strip().lower()

    if not email or not password:
        return False, None

    user = get_user_by_email(email)

    if not user:
        return False, None

    stored_password = user[3]

    # Verify password
    is_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password.encode("utf-8")
    )

    if is_valid:

        user_data = {
            "id": user[0],
            "name": user[1],
            "email": user[2]
        }

        return True, user_data

    return False, None
