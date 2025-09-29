
CREATE OR REPLACE TABLE BUDGET (
    dateMoisAnnee DATE,
    budgetTotal DECIMAL(10, 2),
    PRIMARY KEY (dateMoisAnnee)
);

CREATE OR REPLACE TABLE HABILITATION (
    idHabilitation INT AUTO_INCREMENT,
    nomHabilitation VARCHAR(50),
    PRIMARY KEY (idHabilitation)
);

CREATE OR REPLACE TABLE PERSONNEL (
    idPersonnel VARCHAR(10),
    nom VARCHAR(50),
    prenom VARCHAR(50),
    mdp VARCHAR(50) UNIQUE,
    role ENUM('administratif', 'chercheur', 'technicien','direction'),
    PRIMARY KEY (idPersonnel)
);

CREATE OR REPLACE TABLE POSSEDER_HABILITATION (
    idPersonnel VARCHAR(10),
    idHabilitation INT,
    PRIMARY KEY (idPersonnel, idHabilitation)
);

ALTER TABLE POSSEDER_HABILITATION ADD FOREIGN KEY (idPersonnel) REFERENCES PERSONNEL(idPersonnel);
ALTER TABLE POSSEDER_HABILITATION ADD FOREIGN KEY (idHabilitation) REFERENCES HABILITATION(idHabilitation);


CREATE OR REPLACE TABLE EQUIPEMENT (
    idEquipement INT AUTO_INCREMENT,
    nomEquipement VARCHAR(50),
    PRIMARY KEY (idEquipement)
);

CREATE OR REPLACE TABLE PLATEFORME (
    nomPlateforme VARCHAR(50),
    nbPersonnesRequises INT,
    coutJournalier DECIMAL(10, 2),
    intervalleMaintenance INT,
    PRIMARY KEY (nomPlateforme)
);

CREATE OR REPLACE TABLE INCLURE_EQUIPEMENT (
    nomPlateforme VARCHAR(50),
    idEquipement INT,
    PRIMARY KEY (nomPlateforme, idEquipement)
);  

ALTER TABLE INCLURE_EQUIPEMENT ADD FOREIGN KEY (nomPlateforme) REFERENCES PLATEFORME(nomPlateforme);
ALTER TABLE INCLURE_EQUIPEMENT ADD FOREIGN KEY (idEquipement) REFERENCES EQUIPEMENT(idEquipement);

CREATE OR REPLACE TABLE NECESSITER_HABILITATION (
    idEquipement INT,
    idHabilitation INT,
    PRIMARY KEY (idEquipement, idHabilitation)
);

ALTER TABLE NECESSITER_HABILITATION ADD FOREIGN KEY (idEquipement) REFERENCES EQUIPEMENT(idEquipement);
ALTER TABLE NECESSITER_HABILITATION ADD FOREIGN KEY (idHabilitation) REFERENCES HABILITATION(idHabilitation);

CREATE OR REPLACE TABLE MAINTENANCE (
    nomPlateforme VARCHAR(50),
    dateMaintenance DATE,
    maintenanceTermine BOOLEAN,
    PRIMARY KEY (nomPlateforme, dateMaintenance)
);

ALTER TABLE MAINTENANCE ADD FOREIGN KEY (nomPlateforme) REFERENCES PLATEFORME(nomPlateforme);

CREATE OR REPLACE TABLE CAMPAGNE (
    idCampagne INT AUTO_INCREMENT,
    nomPlateforme VARCHAR(50),
    dateDebut DATE,
    duree INT,
    lieu VARCHAR(100),
    valide BOOLEAN default false,
    PRIMARY KEY (idCampagne)
);

ALTER TABLE CAMPAGNE ADD FOREIGN KEY (nomPlateforme) REFERENCES PLATEFORME(nomPlateforme);

CREATE OR REPLACE TABLE PARTICIPER_CAMPAGNE (
    idPersonnel VARCHAR(10),
    idCampagne INT,
    PRIMARY KEY (idPersonnel, idCampagne)
);

ALTER TABLE PARTICIPER_CAMPAGNE ADD FOREIGN KEY (idPersonnel) REFERENCES PERSONNEL(idPersonnel);
ALTER TABLE PARTICIPER_CAMPAGNE ADD FOREIGN KEY (idCampagne) REFERENCES CAMPAGNE(idCampagne);

CREATE OR REPLACE TABLE ESPECE (
    idEspece INT AUTO_INCREMENT,
    nomEspece VARCHAR(50),
    nomScientifique VARCHAR(100),
    genome TEXT,
    PRIMARY KEY (idEspece)
);

CREATE OR REPLACE TABLE ECHANTILLON (
    idEchantillon INT AUTO_INCREMENT,
    idCampagne INT,
    fichierSequenceADN TEXT,
    idEspece INT,               -- null si non identifié
    commentaire TEXT,
    PRIMARY KEY (idEchantillon)
);

ALTER TABLE ECHANTILLON ADD FOREIGN KEY (idCampagne) REFERENCES CAMPAGNE(idCampagne);
ALTER TABLE ECHANTILLON ADD FOREIGN KEY (idEspece) REFERENCES ESPECE(idEspece);

create or replace index campagneValides ON CAMPAGNE(valide);