# Funciones apoyo
import re
from flask import redirect, render_template, request, session
from functools import wraps


# Login required
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            print("error en user id")
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Validate password
def validate_password(password):
    # Longitud mínima de 8 caracteres
    if len(password) < 8:
        return False

    # Al menos una letra minúscula
    if not re.search("[a-z]", password):
        return False

    # Al menos una letra mayúscula
    if not re.search("[A-Z]", password):
        return False

    # Al menos un dígito
    if not re.search("[0-9]", password):
        return False

    # Al menos un carácter especial
    if not re.search("[!@#$%^&*()-_+=]", password):
        return False

    return True
