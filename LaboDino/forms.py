from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SubmitField,DateField, FloatField
from wtforms.validators import DataRequired
from .models import PERSONNEL,ROLE


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

        # If no user found return None
        if user is None:
            return None

        # Return the user if password matches, else return None
        return user if user.mdp == password else None
    

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