import pytest
from datetime import date
from LaboDino.app import app, db
from LaboDino.models import (
    PERSONNEL, BUDGET, HABILITATION, POSSEDER, EQUIPEMENT, PLATEFORME,
    CAMPAGNE, MAINTENANCE, PARTICIPER_CAMPAGNE, ESPECE, ECHANTILLON,
    inclure_equipement, necessiter_habilitation, ROLE
)

@pytest.fixture
def testapp():

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():

        personnel1 = PERSONNEL("Dupont", "Jean", "mdp123", ROLE.administratif)
        personnel2 = PERSONNEL("Martin", "Sophie", "mdp456", ROLE.chercheur)
        personnel3 = PERSONNEL("Bernard", "Luc", "mdp789", ROLE.technicien)
        personnel4 = PERSONNEL("Dubois", "Marie", "mdp101", ROLE.direction)
        db.session.add_all([personnel1, personnel2, personnel3, personnel4])
        db.session.commit()
        personnel_ids = [p.id_personnel for p in (personnel1, personnel2, personnel3, personnel4)]

        budg1 = BUDGET(date(2024, 1, 1), 50000)
        budg2 = BUDGET(date(2024, 2, 1), 40000)
        budg3 = BUDGET(date(2024, 3, 1), 10000)
        budg4 = BUDGET(date(2024, 6, 1), 20000)
        db.session.add_all([budg1, budg2, budg3, budg4])
        db.session.commit()
        budget_dates = [b.date_mois_annee for b in (budg1, budg2, budg3, budg4)]

        hab_manipulation = HABILITATION("Manipulation ADN")
        hab_sequencage = HABILITATION("Séquençage")
        hab_analyse = HABILITATION("Analyse génomique")
        db.session.add_all([hab_manipulation, hab_sequencage, hab_analyse])
        db.session.commit()
        hab_ids = [h.id_habilitation for h in (hab_manipulation, hab_sequencage, hab_analyse)]

        poss1 = POSSEDER(hab_manipulation.id_habilitation, personnel1.id_personnel)
        poss2 = POSSEDER(hab_sequencage.id_habilitation, personnel2.id_personnel)
        poss3 = POSSEDER(hab_manipulation.id_habilitation, personnel3.id_personnel)
        poss4 = POSSEDER(hab_analyse.id_habilitation, personnel3.id_personnel)
        db.session.add_all([poss1, poss2, poss3, poss4])
        db.session.commit()
        poss_pairs = [(poss1.id_personnel, poss1.id_habilitation),
                      (poss2.id_personnel, poss2.id_habilitation),
                      (poss3.id_personnel, poss3.id_habilitation),
                      (poss4.id_personnel, poss4.id_habilitation)]

        sequenceur = EQUIPEMENT("Séquenceur ADN")
        microscope = EQUIPEMENT("Microscope")
        centrifugeuse = EQUIPEMENT("Centrifugeuse")
        pinceau = EQUIPEMENT("Pinceau")
        db.session.add_all([sequenceur, microscope, centrifugeuse, pinceau])
        db.session.commit()
        equip_ids = [e.id_equipement for e in (sequenceur, microscope, centrifugeuse, pinceau)]

        plateforme_sequence = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
        plateforme_paleontologie = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)
        plateforme_analyse = PLATEFORME("Plateforme Analyse", 4, 1200, 45)
        plat4 = PLATEFORME("Plateforme A", 5, 1500, 90)
        plat5 = PLATEFORME("Plateforme B", 3, 800, 60)
        db.session.add_all([plateforme_sequence, plateforme_paleontologie, plateforme_analyse, plat4, plat5])
        db.session.commit()
        plateforme_names = [p.nom_plateforme for p in (plateforme_sequence, plateforme_paleontologie,
                                                       plateforme_analyse, plat4, plat5)]

        plateforme_sequence.equipements.extend([sequenceur, pinceau])
        plateforme_paleontologie.equipements.append(microscope)
        plateforme_analyse.equipements.append(centrifugeuse)
        db.session.commit()

        sequenceur.habilitations.extend([hab_manipulation, hab_sequencage])
        microscope.habilitations.append(hab_analyse)
        pinceau.habilitations.append(hab_manipulation)
        db.session.commit()

        camp1 = CAMPAGNE(plateforme_sequence.nom_plateforme, date(2024, 1, 15), 2, "Montana, USA", True)
        camp2 = CAMPAGNE(plateforme_paleontologie.nom_plateforme, date(2024, 3, 10), 3, "Patagonie, Argentine", True)
        camp3 = CAMPAGNE(plateforme_analyse.nom_plateforme, date(2024, 6, 1), 4, "Gobi, Mongolie", False)
        db.session.add_all([camp1, camp2, camp3])
        db.session.commit()
        camp_ids = [c.id_campagne for c in (camp1, camp2, camp3)]

        maint1 = MAINTENANCE(plateforme_sequence.nom_plateforme, date(2024, 1, 15), 7)
        maint2 = MAINTENANCE(plateforme_sequence.nom_plateforme, date(2024, 4, 15), 5)
        maint3 = MAINTENANCE(plateforme_paleontologie.nom_plateforme, date(2024, 2, 20), 10)
        db.session.add_all([maint1, maint2, maint3])
        db.session.commit()
        maint_keys = [(maint1.nom_plateforme, maint1.date_maintenance),
                      (maint2.nom_plateforme, maint2.date_maintenance),
                      (maint3.nom_plateforme, maint3.date_maintenance)]

        part_camp1 = PARTICIPER_CAMPAGNE(camp1.id_campagne, personnel1.id_personnel)
        part_camp2 = PARTICIPER_CAMPAGNE(camp2.id_campagne, personnel2.id_personnel)
        part_camp3 = PARTICIPER_CAMPAGNE(camp1.id_campagne, personnel3.id_personnel)
        part_camp4 = PARTICIPER_CAMPAGNE(camp2.id_campagne, personnel3.id_personnel)
        db.session.add_all([part_camp1, part_camp2, part_camp3, part_camp4])
        db.session.commit()
        part_pairs = [(part_camp1.id_campagne, part_camp1.id_personnel),
                      (part_camp2.id_campagne, part_camp2.id_personnel),
                      (part_camp3.id_campagne, part_camp3.id_personnel),
                      (part_camp4.id_campagne, part_camp4.id_personnel)]

        espece1 = ESPECE("T-Rex", "Tyrannosaurus Rex", "AGCT...")
        espece2 = ESPECE("Triceratops", "Triceratops horridus", "GTCA...")
        db.session.add_all([espece1, espece2])
        db.session.commit()
        espece_ids = [espece1.id_espece, espece2.id_espece]

        echantillon1 = ECHANTILLON(camp1.id_campagne, "TRex_dent.adn", "Dent de T-Rex")
        echantillon2 = ECHANTILLON(camp2.id_campagne, "Tric_corne.adn", "Corne de Triceratops")
        db.session.add_all([echantillon1, echantillon2])
        db.session.commit()
        echantillon_ids = [echantillon1.id_echantillon, echantillon2.id_echantillon]

        # Association table snapshots (keys) created
        inclure_keys = [(plateforme_sequence.nom_plateforme, sequenceur.id_equipement),
                        (plateforme_sequence.nom_plateforme, pinceau.id_equipement),
                        (plateforme_paleontologie.nom_plateforme, microscope.id_equipement),
                        (plateforme_analyse.nom_plateforme, centrifugeuse.id_equipement)]
        necessiter_keys = [(sequenceur.id_equipement, hab_manipulation.id_habilitation),
                           (sequenceur.id_equipement, hab_sequencage.id_habilitation),
                           (microscope.id_equipement, hab_analyse.id_habilitation),
                           (pinceau.id_equipement, hab_manipulation.id_habilitation)]

    # Store IDs in closure for teardown
    created = dict(
        personnels=personnel_ids,
        budgets=budget_dates,
        habilitations=hab_ids,
        posseder=poss_pairs,
        equipements=equip_ids,
        plateformes=plateforme_names,
        campagnes=camp_ids,
        maintenances=maint_keys,
        participations=part_pairs,
        especes=espece_ids,
        echantillons=echantillon_ids,
        inclure=inclure_keys,
        necessiter=necessiter_keys,
    )

    yield app

    # Teardown using IDs (no detached instances)
    with app.app_context():
        # Association tables first
        for pf, eq in created["inclure"]:
            db.session.execute(
                inclure_equipement.delete()
                .where(inclure_equipement.c.nomPlateforme == pf)
                .where(inclure_equipement.c.idEquipement == eq)
            )
        for eq, hab in created["necessiter"]:
            db.session.execute(
                necessiter_habilitation.delete()
                .where(necessiter_habilitation.c.idEquipement == eq)
                .where(necessiter_habilitation.c.idHabilitation == hab)
            )
        db.session.commit()

        # Dependent tables
        for camp_id, pers_id in created["participations"]:
            PARTICIPER_CAMPAGNE.query.filter_by(id_campagne=camp_id, id_personnel=pers_id).delete()
        for pers_id, hab_id in created["posseder"]:
            POSSEDER.query.filter_by(id_personnel=pers_id, id_habilitation=hab_id).delete()
        for eid in created["echantillons"]:
            ECHANTILLON.query.filter_by(id_echantillon=eid).delete()
        for pf, d in created["maintenances"]:
            MAINTENANCE.query.filter_by(nom_plateforme=pf, date_maintenance=d).delete()
        for cid in created["campagnes"]:
            CAMPAGNE.query.filter_by(id_campagne=cid).delete()
        db.session.commit()

        # Parents
        for eid in created["especes"]:
            ESPECE.query.filter_by(id_espece=eid).delete()
        for eqid in created["equipements"]:
            EQUIPEMENT.query.filter_by(id_equipement=eqid).delete()
        for hid in created["habilitations"]:
            HABILITATION.query.filter_by(id_habilitation=hid).delete()
        for pf in created["plateformes"]:
            PLATEFORME.query.filter_by(nom_plateforme=pf).delete()
        for d in created["budgets"]:
            BUDGET.query.filter_by(date_mois_annee=d).delete()
        for pid in created["personnels"]:
            PERSONNEL.query.filter_by(id_personnel=pid).delete()
        db.session.commit()

@pytest.fixture
def client(testapp):
    return testapp.test_client()