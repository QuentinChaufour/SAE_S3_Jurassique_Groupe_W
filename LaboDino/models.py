from .app import db
from sqlalchemy import Column, String, Integer, Date, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
    
class Personnel:

    def __init__(self, id_personnel=0, nom="", prenom="", role="", mot_de_passe=""):
        self.id_personnel = id_personnel
        self.nom = nom
        self.prenom = prenom
        self.role = role
        self.mot_de_passe = mot_de_passe
        

class Plateforme(db.Model):
    __tablename__ = 'plateforme'
    
    nom_plateforme = Column(String(50), primary_key=True)
    nb_personnes_requises = Column(Integer)
    cout_journalier = Column(Numeric(10, 2))
    intervalle_maintenance = Column(Integer)
    
    #equipements = relationship('Equipement', back_populates='plateformes')
    #maintenances = relationship('Maintenance', back_populates='plateforme')
    #campagnes = relationship('Campagne', back_populates='plateformes')

    def __init__(self, nom_plateforme="", nb_personnes_requises=0, cout_journalier=0, intervalle_maintenance=0):
        self.nom_plateforme = nom_plateforme
        self.nb_personnes_requises = nb_personnes_requises
        self.cout_journalier = cout_journalier
        self.intervalle_maintenance = intervalle_maintenance

    def __repr__(self):
        return 'Plateforme : ' + self.nom_plateforme
    
