
CREATE TABLE BUDGET (
    dateMoisAnnee DATE,
    budgetTotal DECIMAL(10, 2),
    PRIMARY KEY (dateMoisAnnee)
);

CREATE TABLE HABILITATION (
    idHabilitation INT AUTO_INCREMENT,
    nomHabilitation VARCHAR(50),
    PRIMARY KEY (idHabilitation)
);

CREATE TABLE PERSONNEL (
    idPersonnel INT AUTO_INCREMENT,
    nom VARCHAR(50),
    prenom VARCHAR(50),
    mdp VARCHAR(50) UNIQUE,
    role ENUM('administratif', 'chercheur', 'technicien','direction'),
    PRIMARY KEY (idPersonnel),
);

CREATE TABLE POSSEDER_HABILITATION (
    idPersonnel INT,
    idHabilitation INT,
    PRIMARY KEY (idPersonnel, idHabilitation)
);

ALTER TABLE POSSEDER_HABILITATION ADD FOREIGN KEY (idPersonnel) REFERENCES PERSONNEL(idPersonnel);
ALTER TABLE POSSEDER_HABILITATION ADD FOREIGN KEY (idHabilitation) REFERENCES HABILITATION(idHabilitation);


CREATE TABLE EQUIPEMENT (
    idEquipement INT AUTO_INCREMENT,
    nomEquipement VARCHAR(50),
    PRIMARY KEY (idEquipement)
);

CREATE TABLE PLATEFORME (
    nomPlateforme VARCHAR(50),
    nbPersonnesRequises INT,
    coutJournalier DECIMAL(10, 2),
    intervalleMaintenance INT,
    derniereMaintenance INT,
    PRIMARY KEY (nomPlateforme)
);

CREATE TABLE INCULRE_EQUIPEMENT (
    nomPlateforme VARCHAR(50),
    idEquipement INT,
    PRIMARY KEY (nomPlateforme, idEquipement)
);

ALTER TABLE INCULRE_EQUIPEMENT ADD FOREIGN KEY (nomPlateforme) REFERENCES PLATEFORME(nomPlateforme);
ALTER TABLE INCULRE_EQUIPEMENT ADD FOREIGN KEY (idEquipement) REFERENCES EQUIPEMENT(idEquipement);

CREATE TABLE NECESSITER_HABILITATION (
    nomPlateforme VARCHAR(50),
    idHabilitation INT,
    PRIMARY KEY (nomPlateforme, idHabilitation)
);

ALTER TABLE NECESSITER_HABILITATION ADD FOREIGN KEY (nomPlateforme) REFERENCES PLATEFORME(nomPlateforme);
ALTER TABLE NECESSITER_HABILITATION ADD FOREIGN KEY (idHabilitation) REFERENCES HABILITATION(idHabilitation);

CREATE TABLE MAINTENANCE (
    nomPlateforme VARCHAR(50),
    idPersonnel INT,
    dateMaintenance DATE,
    dureeMaintenance INT,
    PRIMARY KEY (nomPlateforme, dateMaintenance)
);

ALTER TABLE MAINTENANCE ADD FOREIGN KEY (nomPlateforme) REFERENCES PLATEFORME(nomPlateforme);
ALTER TABLE MAINTENANCE ADD FOREIGN KEY (idPersonnel) REFERENCES PERSONNEL(idPersonnel);

CREATE TABLE CAMPAGNE (
    idCampagne INT AUTO_INCREMENT,
    nomPlateforme VARCHAR(50),
    dateDebut DATE,
    duree INT,
    lieu VARCHAR(100),
    PRIMARY KEY (idCampagne)
);

ALTER TABLE CAMPAGNE ADD FOREIGN KEY (nomPlateforme) REFERENCES PLATEFORME(nomPlateforme);

CREATE TABLE PARTICIPER_CAMPAGNE (
    idPersonnel INT,
    idCampagne INT,
    PRIMARY KEY (idPersonnel, idCampagne)
);

ALTER TABLE PARTICIPER_CAMPAGNE ADD FOREIGN KEY (idPersonnel) REFERENCES PERSONNEL(idPersonnel);
ALTER TABLE PARTICIPER_CAMPAGNE ADD FOREIGN KEY (idCampagne) REFERENCES CAMPAGNE(idCampagne);

CREATE TABLE ESPECE (
    idEspece INT AUTO_INCREMENT,
    nomEspece VARCHAR(50),
    nomScientifique VARCHAR(100),
    genome TEXT,
    PRIMARY KEY (idEspece)
);

CREATE TABLE ECHANTILLON (
    idEchantillon INT AUTO_INCREMENT,
    idCampagne INT,
    fichierSequenceADN TEXT,
    idEspece INT,               -- null si non identifié
    commentaire TEXT,
    PRIMARY KEY (idEchantillon)
);

ALTER TABLE ECHANTILLON ADD FOREIGN KEY (idCampagne) REFERENCES CAMPAGNE(idCampagne);
ALTER TABLE ECHANTILLON ADD FOREIGN KEY (idEspece) REFERENCES ESPECE(idEspece);






