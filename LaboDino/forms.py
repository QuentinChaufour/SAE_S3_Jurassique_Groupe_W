from datetime import date, datetime
from flask_wtf import FlaskForm
from .app import db
from wtforms import HiddenField, StringField, PasswordField, SubmitField,DateField, FloatField, IntegerField
from wtforms.validators import DataRequired
from .models import MAINTENANCE, PERSONNEL, PLATEFORME,ROLE
from sqlalchemy.exc import IntegrityError
from flask import flash,redirect, url_for,request

class LoginForm(FlaskForm):
    """Form for user login."""

    id = StringField('Identifier', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    next = HiddenField()
    submit = SubmitField('Login')

    def authenticate(self):
        
        id: int = int(self.id.data)
        password: str = self.password.data

        user = PERSONNEL.query.filter_by(id_personnel=id).first()
        #user = Personnel.query.filter_by(nom=name, prenom=firstname)
        if user:
            print(f"User found: {user.nom} {user.prenom}")
            print(f"Password in DB: '{user.mdp}'")
            print(f"Password entered: '{password}'")
            print(f"Match: {user.mdp == password}")
        else:
            print(f"No user found with ID: {id}")
        # If no user found return None
        if user is None:
            return None

        # Return the user if password matches, else return None
        return user if user.mdp == password else None
    
class PlatformForm(FlaskForm):
    nom_plateforme = StringField('Nom Plateforme', validators=[DataRequired()])
    nb_personnes_requises = IntegerField('Nombre Personnes Requises', validators=[DataRequired()])
    cout_journalier = FloatField('Cout Journalier', validators=[DataRequired()])
    intervalle_maintenance = IntegerField('Intervalle Maintenance', validators=[DataRequired()])
    submit = SubmitField('Créer la plateforme')

    def create_platform(self, filtre):
        platform = PLATEFORME.query.filter_by(nom_plateforme=self.nom_plateforme.data).first()
        if not platform:
            try:
                platform = PLATEFORME(
                    nom_plateforme=self.nom_plateforme.data,
                    nb_personnes_requises=self.nb_personnes_requises.data,
                    cout_journalier=self.cout_journalier.data,
                    intervalle_maintenance=self.intervalle_maintenance.data
                )
                db.session.add(platform)
                print(platform)
                db.session.commit()
                flash("Plateforme créée avec succès !")
            except IntegrityError as e:
                print(f"Database error occurred while creating platform: {e}")
                flash("Erreur avec la base de donnée lors de la création de la plateforme", "error")
        else:
            flash("Impossible de créer deux plateformes qui portent le même nom !", "error")
        return redirect(url_for('platform_management', filtre=filtre))
    
    def modify_platform(self):
        platform = PLATEFORME.query.filter_by(nom_plateforme=self.nom_plateforme.data).first()
        print("PLATEFORME ", PLATEFORME.query.filter_by(nom_plateforme=self.nom_plateforme.data).first())
        platform.nb_personnes_requises = self.nb_personnes_requises.data
        platform.cout_journalier = self.cout_journalier.data
        platform.intervalle_maintenance = self.intervalle_maintenance.data
        print(platform)
        db.session.commit()
        flash("Plateforme modifiée avec succès")
        return redirect(url_for('platform_detail', platform_name=self.nom_plateforme.data))


class MaintenanceForm(FlaskForm):
    date_maintenance = DateField('Date', validators=[DataRequired()])
    duree_maintenance = IntegerField('Duree', validators=[DataRequired()])
    nom_plateforme = StringField('Nom plateforme', validators=[DataRequired()])
    submit = SubmitField('Créer la maintenance')

    def create_maintenance(self, filtre):
        try:
            plateforme = PLATEFORME.query.filter_by(nom_plateforme=self.nom_plateforme.data).first()
            maintenance = MAINTENANCE.query.filter_by(
                nom_plateforme=self.nom_plateforme.data, 
                date_maintenance=self.date_maintenance.data
            ).first()        
            if not plateforme:
                flash("La plateforme que vous essayez de renseigner n'existe pas.", "error")
            elif self.date_maintenance.data < date.today():
                flash("Impossible de créer une maintenance avec une date passée", "error")
            elif maintenance:
                flash("Impossible de créer deux maintenances débutant le même jour pour la même plateforme", "error")
            else:
                maintenance = MAINTENANCE(
                    nom_plateforme=self.nom_plateforme.data,
                    date_maintenance=self.date_maintenance.data,
                    duree_maintenance=self.duree_maintenance.data,
                )
                db.session.add(maintenance)
                print(maintenance)
                db.session.commit()
                flash("Maintenance créée avec succès !")
        except IntegrityError as e:
            print(f"Database error occurred while creating platform: {e}")
            flash("Erreur avec la base de donnée lors de la création de la plateforme", "error")

        return redirect(url_for('maintenance_management', filtre=filtre))
        
    def modify_maintenance(self, platform_name, date_maintenance):
        date = datetime.strptime(date_maintenance, '%Y-%m-%d').date()
        try:
            maintenance = MAINTENANCE.query.filter_by(nom_plateforme=self.nom_plateforme.data, date_maintenance=date).first()
            if maintenance:
                if self.date_maintenance.data < date.today():
                    flash("Impossible de créer une maintenance avec une date passée", "error")
                    return redirect(url_for('maintenance_detail', 
                                    platform_name=self.nom_plateforme.data,
                                    date_maintenance=self.date_maintenance.data.strftime('%Y-%m-%d')))
                db.session.delete(maintenance)
                db.session.commit()
                
                nouvelle_maintenance = MAINTENANCE(
                    nom_plateforme=self.nom_plateforme.data,
                    date_maintenance=self.date_maintenance.data,
                    duree_maintenance=self.duree_maintenance.data
                )
                db.session.add(nouvelle_maintenance)
                db.session.commit()
                flash("Maintenance modifiée avec succès !")
                return redirect(url_for('maintenance_detail', 
                                    platform_name=self.nom_plateforme.data,
                                    date_maintenance=self.date_maintenance.data.strftime('%Y-%m-%d')))
            else:
                flash("Maintenance introuvable.", "error")
                
        except IntegrityError as e:
            print(f"Database error occurred while creating platform: {e}")
            flash("Erreur avec la base de donnée lors de la création de la plateforme", "error")

class BudgetForm(FlaskForm):
    """Form for defining a budget."""

    date : DateField = DateField('Budget month', validators=[DataRequired()])
    montant : FloatField = FloatField('Montant', validators=[DataRequired()],description="Enter the budget amount in numeric format.")

    submit : SubmitField = SubmitField('Define Budget')

    def add_budget(self) -> tuple[str, float]:
        montant_value: float = self.montant.data
        date_value = self.date.data
        # Gestion des erreurs
        
        return date_value, montant_value
