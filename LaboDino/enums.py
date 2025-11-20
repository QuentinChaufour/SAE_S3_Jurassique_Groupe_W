from enum import Enum

class UserRole(Enum):
    """Enumération des rôles utilisateur dans l'application LaboDino."""
    
    DIRECTION = "direction"
    ADMIN = "admin"
    RESEARCHER = "researcher"
    TECHNICIAN = "technician"