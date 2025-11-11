from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SubmitField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.validators import DataRequired
from hashlib import sha256

from LaboDino.models import Personnel

class LoginForm(FlaskForm):

    id = StringField('Name and Forename', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Login')

    def authenticate(self):
        
        name: str = self.id.data.split(" ")[0]
        firstname: str = self.id.data.split(" ")[1]
        password_hashed: str = sha256(self.password.data.encode('utf-8')).hexdigest()

        user = Personnel.query.filter_by(nom=name, prenom=firstname)

        # If no user found return None
        if user is None:
            return None

        # Return the user if password matches, else return None
        return user if user.mot_de_passe == password_hashed else None
    
class PlatformCreationForm(FlaskForm):
    nom_plateforme = StringField('Nom Plateforme', validators=[DataRequired()])
    nb_personnes_requises = IntegerField('Nombre Personnes Requises', validators=[DataRequired()])
    cout_journalier = FloatField('Cout Journalier', validators=[DataRequired()])
    intervalle_maintenance = IntegerField('Intervalle Maintenance', validators=[DataRequired()])
    submit = SubmitField('Créer la plateforme')