from .app import login_manager, users_storage
from flask_login import UserMixin

class Personnel(UserMixin):

    def __init__(self, id_personnel = 0, nom = "", prenom = "", role = "", mot_de_passe = ""):
        self.id = id_personnel
        self.nom = nom
        self.prenom = prenom
        self.role = role
        self.mot_de_passe = mot_de_passe

    def getRole(self) -> str:
        return self.role
    
@login_manager.user_loader
def load_user(user_id):
    return users_storage.get(int(user_id))