
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
    idPersonnel VARCHAR(10),
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
    coutJournalier DECIMAL(5, 2),
    intervalleMaintenance INT,
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
    idEquipement INT,
    idHabilitation INT,
    PRIMARY KEY (idEquipement, idHabilitation)
);

ALTER TABLE NECESSITER_HABILITATION ADD FOREIGN KEY (idEquipement) REFERENCES EQUIPEMENT(idEquipement);
ALTER TABLE NECESSITER_HABILITATION ADD FOREIGN KEY (idHabilitation) REFERENCES HABILITATION(idHabilitation);

CREATE TABLE MAINTENANCE (
    nomPlateforme VARCHAR(50),
    dateMaintenance DATE,
    maintenanceTermine BOOLEAN,
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



delimiter |

create or replace function remainingBudget(moment Date) returns DECIMAL(10,2)
begin
    declare initialBudget DECIMAL(10,2);

    declare monthSearched INT default MONTH(moment);
    declare yearSearched INT default YEAR(moment);

    declare coutCampagne DECIMAL(10,2);
    declare budgetUtilise DECIMAL(10,2);
    declare fini default false;
    declare lesCouts cursor for 
        SELECT coutJournalier * duree 
        FROM CAMPAGNE NATURAL JOIN PLATEFORME
        WHERE MONTH(dateDebut) = monthSearched AND YEAR(dateDebut) = yearSearched;

    declare continue handler for not found set fini = true; 

    -- récupération du budget initiale du mois courrant a la date souhaité
    SELECT budget into initialBudget
    FROM BUDGET
    WHERE YEAR(dateMoisAnnee) = yearSearched AND MONTH(dateMoisAnnee) = monthSearched;

    -- somme des couts des campagne du mois courrant a la date souhaité

    open lesCouts
    while not fini do 
        fetch lesCouts into coutCampagne;
        if not fini then
            set budgetUtilise = budgetUtilise + coutCampagne;
        end if;
    end while;

    return initialBudget - coutCampagne;
end |

create or replace function plateformeAvailable(moment date,plateforme VARCHAR(50)) returns boolean
begin
    declare isAvailable boolean default true;
    declare dureeCampagne INT;
    declare dateCampagne DATE;

    declare fini default false;
    declare lesCampagnes cursor for 
        SELECT dateDebut,duree
        FROM CAMPAGNE
        WHERE nomPlateforme = plateforme AND MONTH(moment) = MONTH(dateDebut) AND YEAR(moment) = YEAR(dateDebut); 

    open lesCampagnes
    while not fini do

        fetch lesCampagnes into dateCampagne,dureeCampagne;


    end while;

end |

-- Triggers

create or replace TRIGGER checkCampagneValidity
before INSERT ON CAMPAGNE FOR EACH ROW 
begin
    declare budgetRestant DECIMAL(10,2) default SELECT remainingBudget(new.dateDebut);
    declare coutPlatefrom DECIMAL(10,2);

    declare messageErreur VARCHAR(50); 

    -- récupération du cout journalier de la plateforme 
    -- utilisé pour la nouvelle campagne
    SELECT coutJournalier into coutPlatefrom
    FROM PLATEFORME
    WHERE nomPlateforme = new.nomPlateforme;

    -- vérification de la validité des couts de la campagne 
    if new.duree * coutJournalier > budgetRestant then
        set messageErreur = CONCAT('Coût dépassant du budget restant :  ',new.duree * coutJournalier,' coût de la plateforme    |   ',budgetRestant,'  budget restant.');
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;

    -- verification de validité d'utilisation de la plateforme 


end |

delimiter ;


 


