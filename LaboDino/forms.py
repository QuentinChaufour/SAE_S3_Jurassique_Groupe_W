from .app import db,app
from .models import PERSONNEL,ROLE,PLATEFORME, CAMPAGNE,PARTICIPER_CAMPAGNE
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SubmitField,DateField, FloatField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired
from flask_login import current_user


class LoginForm(FlaskForm):
    """Form for user login."""

    id = StringField(label='Identifier', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    next = HiddenField()
    submit = SubmitField(label='Login')

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

    date : DateField = DateField(label='Budget month',
                                 validators=[DataRequired()])
    montant : FloatField = FloatField(label='Montant',
                                      validators=[DataRequired()],description="Enter the budget amount in numeric format.")

    submit : SubmitField = SubmitField(label='Define Budget')

    def add_budget(self) -> tuple[str, float]:
        montant_value: float = self.montant.data
        date_value = self.date.data
        # Gestion des erreurs
        
        return date_value, montant_value
    
class CampaignForm(FlaskForm):
    """Form for creating or editing a campaign."""
    with app.app_context():
        plateforme_choices: list[PLATEFORME] = PLATEFORME.query.all()

    lieu : StringField = StringField(label='Lieu de la campagne : ',
                                     validators=[DataRequired()])
    plateforme : SelectField = SelectField(label='Plateforme :',
                                           choices=[plateform.nom_plateforme for plateform in plateforme_choices], 
                                           validators=[DataRequired()])
    startDate : DateField = DateField(label='Début de la campagne :',
                                      validators=[DataRequired()])
    duree : IntegerField = IntegerField(label='Durée (en jours) :',
                                         validators=[DataRequired()])
    participate: BooleanField = BooleanField(label='Participer ?')
    submit : SubmitField = SubmitField(label='Submit Campaign')

    def create_campaign(self) -> None:
        """Create a new campaign."""
        plateforme_value: str = self.plateforme.data
        lieu_value: str = self.lieu.data
        startDate_value = self.startDate.data
        duree_value: int = self.duree.data
        participate_value: bool = self.participate.data

        new_campaign: CAMPAGNE = CAMPAGNE(
            nom_plateforme=plateforme_value,
            dateDebut=startDate_value,
            duree=duree_value,
            lieu=lieu_value,
        )

        db.session.add(new_campaign)
        db.session.commit()

        # If the user wants to participate, add him to the list of participants
        if participate_value and current_user.is_authenticated:
            participate: PARTICIPER_CAMPAGNE = PARTICIPER_CAMPAGNE(
                id_personnel=current_user.id_personnel,
                id_campagne=new_campaign.id_campagne
            )
            db.session.add(participate)
            db.session.commit()

    def update(self, campaign_id: int) -> None:
        """Update an existing campaign."""
        campagne: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()

        if campagne:
            try:
                campagne.nom_plateforme = self.plateforme.data
                campagne.lieu = self.lieu.data
                campagne.dateDebut = self.startDate.data
                campagne.duree = self.duree.data
                db.session.add(campagne)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error updating campaign: {e}")
        else:
            print(f"Campaign with ID {campaign_id} not found.")

