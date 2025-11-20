from .app import login_manager, users_storage
from .enums import UserRole
from flask_login import UserMixin

class Personnel(UserMixin):

    def __init__(self, id_personnel: str = "0", nom: str = "", prenom: str = "", role: UserRole = UserRole.RESEARCHER, mot_de_passe: str = ""):
        self.id = id_personnel
        self.nom = nom
        self.prenom = prenom
        self.role = role
        self.mot_de_passe = mot_de_passe

    def getRole(self) -> UserRole:
        return self.role
    
@login_manager.user_loader
def load_user(user_id):
    """Load user selon son ID"""
    return users_storage.get(int(user_id))