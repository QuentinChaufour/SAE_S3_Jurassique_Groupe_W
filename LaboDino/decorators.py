from .models import ROLE

from flask_login import current_user
from flask import redirect, url_for
from typing import Callable
from functools import wraps

# link for reference:
#https://codefinity.com/blog/How-to-use-Decorators-in-Python?utm_source=google&utm_medium=cpc&utm_campaign=21193856569&utm_content=&utm_term=&dki=&gad_source=1&gad_campaignid=21183361821&gbraid=0AAAAABTeUgQlF9iFKUqehkOcdJf0x0Ssx&gclid=CjwKCAiAz_DIBhBJEiwAVH2XwFCr9Ao896ypVuupmtsDtZakq6SbO0qs98ZypSOBYNH2TmqzJ78eAhoCFUAQAvD_BwE

def role_access_rights(*role: ROLE):
    """décorateur vérifiant si l'utilisateur a les droits d'accès en fonction de son rôle.
    
    Args:
        *role (UserRole): Les rôles requis pour accéder à la vue.

    Returns:
        function: La fonction décorée avec les droits d'accès vérifiés.
        redirect: Redirige vers la page d'accueil de l'utilisateur si les droits d'accès sont insuffisants.
    """

    def wrapper(f: Callable):
        # preserve les métadonnées produites par flask avec les routes
        @wraps(f)
        def decorated_function(*args, **kwargs):
            """Vérifie les droits d'accès de l'utilisateur avant d'exécuter la fonction décorée."""

            if not current_user.is_authenticated:
                return redirect(url_for("login"))

            if current_user.get_role() not in role:
                print("Access denied: insufficient rights.")

                return redirect(url_for("login"))
                #return redirect(url_for("home_" + current_user.getRole().value()))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
    