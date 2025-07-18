# app/decorators.py

from functools import wraps
from flask import session, redirect, url_for, flash, render_template


def roles_required(*roles):
    """Allow access only to users with specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('role')
            if user_role not in roles:
                flash("Unauthorized access.", "danger")
                return render_template("403.html"), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
