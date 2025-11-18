from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired
from hashlib import sha256
import datetime

from LaboDino.models import PERSONNEL


class LoginForm(FlaskForm):
    """Form for user login."""

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
    

class BudgetForm(FlaskForm):
    """Form for defining a budget."""

    date : HiddenField = HiddenField('Date', validators=[DataRequired()])
    montant : FloatField = FloatField('Montant', validators=[DataRequired()],description="Enter the budget amount in numeric format.")

    submit : SubmitField = SubmitField('Define Budget')

    def add_budget(self) -> tuple[str, float]:
        date_value: str = datetime.datetime.strptime(self.date.data, "%Y-%m").date().strftime("%Y-%m")
        montant_value: float = self.montant.data

        # Gestion des erreurs
        
        return date_value, montant_value