from .app import db,app
from .models import PERSONNEL,ROLE,PLATEFORME, CAMPAGNE,PARTICIPER_CAMPAGNE,ESPECE,ECHANTILLON, EQUIPEMENT, HABILITATION
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SubmitField,DateField, FloatField, IntegerField, BooleanField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_login import current_user
from sqlalchemy.exc import OperationalError


class LoginForm(FlaskForm):
    """Form for user login."""

    id: StringField = StringField(label='Identifier', validators=[DataRequired()])
    password: PasswordField= PasswordField(label='Password', validators=[DataRequired()])
    next: HiddenField = HiddenField()
    submit: SubmitField = SubmitField(label='Login')

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

    lieu : StringField = StringField(label='Lieu de la campagne : ',
                                     validators=[DataRequired()])
    plateforme : SelectField = SelectField(label='Plateforme :',
                                           choices=[], 
                                           validators=[DataRequired()])
    startDate : DateField = DateField(label='Début de la campagne :',
                                      validators=[DataRequired()])
    duree : IntegerField = IntegerField(label='Durée (en jours) :',
                                         validators=[DataRequired()])
    participate: BooleanField = BooleanField(label='Participer ?', false_values=("false", "0",0, "", None), default=False)
    submit : SubmitField = SubmitField(label='Submit Campaign')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plateforme.choices = [
            p.nom_plateforme for p in PLATEFORME.query.all()
        ]

    def create_campaign(self) -> None|OperationalError:
        """Create a new campaign."""
        plateforme_value: str = self.plateforme.data
        lieu_value: str = self.lieu.data
        startDate_value = self.startDate.data
        duree_value: int = self.duree.data
        participate_value: bool = self.participate.data

        try:
            new_campaign: CAMPAGNE = CAMPAGNE(
                nom_plateforme=plateforme_value,
                dateDebut=startDate_value,
                duree=duree_value,
                lieu=lieu_value,
            )
    
            

            if participate_value and current_user.is_authenticated:
                participate: PARTICIPER_CAMPAGNE = PARTICIPER_CAMPAGNE(
                    id_personnel=current_user.id_personnel,
                    id_campagne=new_campaign.id_campagne
                )
                new_campaign.participerCampagne.append(participate)
                db.session.add(participate)

            db.session.add(new_campaign)
            db.session.commit()

        except OperationalError as e:
            db.session.rollback()
            raise e

    def update(self, campaign_id: int) -> None|OperationalError:
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
            except OperationalError as e:
                db.session.rollback()
                raise e
        else:
            print(f"Campaign with ID {campaign_id} not found.")

class SampleForm(FlaskForm):
    """Form for adding or editing a sample."""

    comment : TextAreaField = TextAreaField(label='Comment : ')
    
    dna_file : FileField = FileField(label='DNA File : ',
                                     validators=[DataRequired()])
    
    specie : SelectField = SelectField(label='Specie : ',
                                       choices=[],
                                       coerce=lambda v: None if v in (None, "", "None") else int(v),
                                       )

    submit : SubmitField = SubmitField(label='Add Sample')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.specie.choices = [(None,"")] + [
            (specie.id_espece, specie.nom_espece) for specie in ESPECE.query.all()
        ]

    def create_sample(self, campaign_id: int) -> None| OperationalError:

        campaign: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()
        if campaign is None or not campaign.valide:
            raise OperationalError("Cannot add sample to an invalid or non-existent campaign.")
        
        comment_value: str = self.comment.data
        dna_file_value: str = self.dna_file.data
        specie_value: int = self.specie.data

        id_specie: int = None

        if specie_value is not None:
            id_specie = specie_value

        new_sample: ECHANTILLON = ECHANTILLON(
            id_campagne=campaign_id,
            commentaire=comment_value,
            fichier_sequence_adn=dna_file_value,
            id_espece=id_specie)
        
        db.session.add(new_sample)
        db.session.commit()

        # TODO : Handle file upload properly

    def update(self, sample_id: int) -> None| OperationalError:
        """Update an existing sample."""
        sample: ECHANTILLON = ECHANTILLON.query.filter_by(id_echantillon=sample_id).first()

        if sample:
            sample.commentaire = self.comment.data
            sample.fichier_sequence_adn = self.dna_file.data

            if self.specie.data is not None:
                sample.id_espece = self.specie.data
                
            db.session.add(sample)
            db.session.commit()

        else:
            raise OperationalError(f"Sample with ID {sample_id} not found.")


class EquipmentForm(FlaskForm):
    """
    Form for ceating and updating equipments
    """
    name: StringField = StringField(label="nom", validators=[DataRequired()])
    plateform: SelectField =  SelectField(label="Plateforme", 
                                          choices= [],
                                          coerce=lambda v: None if v in (None, "", "None") else v
                                          )
    habilitation: SelectField = SelectField(label="Habilitation required", 
                                            choices=[],
                                            coerce=lambda v: None if v in (None, "", "None") else int(v)
                                            )
    submit: SubmitField = SubmitField(label="Créer equipement")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plateform.choices = [(None,"")] + [
            (p.nom_plateforme, p.nom_plateforme) for p in PLATEFORME.query.all()
        ]
        self.habilitation.choices = [(None, "")] + [
            (h.id_habilitation, h.nom_habilitation) for h in HABILITATION.query.all()
        ]

    def create_equipment(self) -> None:
        """ Create a new equipment"""
        
        equipment: EQUIPEMENT = EQUIPEMENT(nom_equipement= self.name.data)
        db.session.add(equipment)

        if self.plateform.data != None:
            used_plateform: PLATEFORME = PLATEFORME.query.filter_by(nom_plateforme= self.plateform.data).first()
            equipment.plateformes.append(used_plateform)

        if self.habilitation.data != None:
            habilitation: HABILITATION = HABILITATION.query.get(int(self.habilitation.data))
            equipment.habilitations.append(habilitation)

        db.session.commit()

    def update(self, id_equipment: int) -> None| OperationalError:
        """ Update an existing equipment """
        
        equipment: EQUIPEMENT = EQUIPEMENT.query.filter_by(id_equipement= id_equipment).first()

        if equipment is not None:
            try:

                equipment.nom_equipement = self.name.data

                if self.plateform.data:

                    if self.plateform.data == None:
                        equipment.plateformes.clear()

                    else:
                        equipment.plateformes.clear()
                        used_plateform: PLATEFORME = PLATEFORME.query.filter_by(nom_plateforme= self.plateform.data).first()
                    
                        if used_plateform: equipment.plateformes.append(used_plateform)

                if self.habilitation.data:

                    if self.habilitation.data == None:
                        equipment.habilitations.clear()    

                    else:
                        equipment.habilitations.clear()
                        habilitation: HABILITATION = HABILITATION.query.filter_by(id_habilitation=int(self.habilitation.data)).first()

                        if habilitation: equipment.habilitations.append(habilitation)

                db.session.commit()

            except OperationalError as e:
                db.session.rollback()
                raise e

        else:
            raise OperationalError(f"Equipment with ID {id_equipment} not found.")
