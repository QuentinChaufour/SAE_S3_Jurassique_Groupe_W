delimiter |

create or replace function remainingBudget(moment Date) returns DECIMAL(10,2)
begin
    declare initialBudget DECIMAL(10,2);

    declare coutCampagne DECIMAL(10,2);
    declare budgetUtilise DECIMAL(10,2) default 0;
    declare fini boolean default false;
    declare lesCouts cursor for 
        SELECT coutJournalier * duree 
        FROM CAMPAGNE NATURAL JOIN PLATEFORME
        WHERE MONTH(dateDebut) = MONTH(moment) AND YEAR(dateDebut) = YEAR(moment) AND (valide = true OR dateDebut < CURDATE());

    declare continue handler for not found set fini = true; 

    -- récupération du budget initiale du mois courrant a la date souhaité
    SELECT budgetTotal into initialBudget
    FROM BUDGET
    WHERE YEAR(dateMoisAnnee) = YEAR(moment) AND MONTH(dateMoisAnnee) = MONTH(moment);

    -- somme des couts des campagne du mois courrant a la date souhaité

    open lesCouts;
    while not fini do 
        fetch lesCouts into coutCampagne;
        if not fini then
            set budgetUtilise = budgetUtilise + coutCampagne;
        end if;
    end while;

    return IFNULL(initialBudget - budgetUtilise,0);
end |

create or replace function plateformeAvailable(moment date,plateforme VARCHAR(50)) returns boolean
begin
    declare isAvailable boolean default true;
    declare dureeCampagne INT;
    declare dateCampagne DATE;

    declare fini boolean default false;
    declare lesCampagnes cursor for 
        SELECT dateDebut,duree
        FROM CAMPAGNE
        WHERE nomPlateforme = plateforme AND MONTH(moment) = MONTH(dateDebut) AND YEAR(moment) = YEAR(dateDebut); 

    declare continue handler for not FOUND set fini = true;

    open lesCampagnes;
    while not fini do

        fetch lesCampagnes into dateCampagne,dureeCampagne;

        if not fini then

            if (DATEDIFF(dateCampagne,moment) < dureeCampagne) AND dateCampagne > moment then
                set isAvailable = false;
            end if;
        end if;
    end while;
    return isAvailable;
end |

create or replace function plateformeInMaintenace(dateUtilisation Date,dureeUtilisation int,nomPlateformeUtilise VARCHAR(50)) returns boolean
begin
    declare isInMaintenance boolean default true;
    declare dureeLastMaintenance int;
    declare dateLastMaintenance date;
    declare utilisation int;
    declare maxUtilisation int;

    SELECT dateMaintenance,dureeMaintenance into dateLastMaintenance,dureeLastMaintenance
    FROM MAINTENANCE
    WHERE nomPlateforme = nomPlateformeUtilise AND dateMaintenance >= ALL(
        SELECT dateLastMaintenance
        FROM MAINTENANCE
        WHERE nomPlateforme = nomPlateformeUtilise
    );

    SELECT SUM(duree) into utilisation
    FROM CAMPAGNE
    WHERE nomPlateforme = nomPlateformeUtilise AND dateDebut > dateLastMaintenance;

    SELECT intervalleMaintenance into maxUtilisation
    FROM PLATEFORME
    WHERE nomPlateforme = nomPlateformeUtilise;
    -- plateforme en maintenance ?
    if (DATE_ADD(dateLastMaintenance, INTERVAL dureeLastMaintenance DAY) < dateUtilisation) then
        set isInMaintenance = false;
    end if;
    -- plateforme nécessitera une maintenance au cours de la campagne ?
    if (utilisation + dureeUtilisation < maxUtilisation) then
        set isInMaintenance = false;
    end if;

    return isInMaintenance;
end |

create or replace function verifyHabilitationValidity(idCampagneEnrolledIn INT,idHabilitationRequired INT) returns BOOLEAN
begin
    declare isRepresented BOOLEAN default false;
    declare habilitation INT;
    declare fini BOOLEAN default false;
    declare getHabilitationsRepresented cursor for 
        SELECT idHabilitation
        FROM PARTICIPER_CAMPAGNE NATURAL JOIN POSSEDER_HABILITATION
        WHERE idCampagne = idCampagneEnrolledIn;

    declare continue handler for not found set fini = true;

    open getHabilitationsRepresented;
    while not fini do
        fetch getHabilitationsRepresented into habilitation;

        if (not fini AND habilitation = idHabilitationRequired) then
            set isRepresented = true;
        end if;
    end while;
    close getHabilitationsRepresented;
    return isRepresented;
end |

-- Triggers

create or replace TRIGGER checkBudget
before INSERT ON BUDGET FOR EACH ROW
begin
    declare messageErreur VARCHAR(100); 

    -- vérifie que le budget n'est pas négatif
    if (new.budgetTotal < 0) then
        set messageErreur = 'Le budget ne peut pas être négatif';
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;

    -- vérifie qu'il n'y a pas déjà un budget pour le mois et l'année indiqués
    if exists(SELECT * FROM BUDGET WHERE YEAR(dateMoisAnnee) = YEAR(new.dateMoisAnnee) AND MONTH(dateMoisAnnee) = MONTH(new.dateMoisAnnee)) then
        set messageErreur = 'Un budget est déjà indiqué pour le mois et l''année spécifiés';
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;
end |

create or replace TRIGGER checkBudgetUpdate
before UPDATE ON BUDGET FOR EACH ROW
begin
    declare messageErreur VARCHAR(200); 
    declare fondsEngage DECIMAL(10,2);
    declare totalFondsEngage DECIMAL(10,2) default 0;
    declare currentDate Date default CURDATE();

    declare fini boolean default false;
    declare lesFondsEngage cursor for
        SELECT coutJournalier * duree 
        FROM CAMPAGNE NATURAL JOIN PLATEFORME
        WHERE MONTH(dateDebut) = MONTH(new.dateMoisAnnee) AND YEAR(dateDebut) = YEAR(new.dateMoisAnnee);

    declare continue handler for not found set fini = true;
    -- vérifie que le budget n'est pas négatif
    if (new.budgetTotal < 0) then
        set messageErreur = 'Le budget ne peut pas être négatif';
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;

    -- verifie que le budget voulant être modifié n'est pas pour un mois passé
    if(MONTH(old.dateMoisAnnee) < MONTH(currentDate) AND YEAR(old.dateMoisAnnee) < YEAR(currentDate)) then
        set messageErreur = 'La date budget indiqué dépassé, modification annulé';
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;

    -- vérifie que les fonds engagé sont inférieur au nouveau budget
    open lesFondsEngage;
    while not fini do
        fetch lesFondsEngage into fondsEngage;
        if not fini then
            set totalFondsEngage = totalFondsEngage + fondsEngage;
        end if;
    end while;

    if (totalFondsEngage > new.budgetTotal) then
        set messageErreur = 'Le budget indiqué est inférieur aux fonds actuellement engagé sur les différentes campagne, modification annulé';
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;
end |

create or replace trigger checkDelBudget
before DELETE on BUDGET for each row
begin
    declare messageErreur VARCHAR(500);
    
    if exists(SELECT * FROM CAMPAGNE WHERE MONTH(dateDebut) = MONTH(old.dateMoisAnnee) and YEAR(dateDebut) = YEAR(old.dateMoisAnnee)) then
        set messageErreur = "Impossible de supprimer le budget car il y a une campagne en cours";
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;
end |

create or replace TRIGGER checkCampagne
before INSERT ON CAMPAGNE FOR EACH ROW 
begin
    declare budgetRestant DECIMAL(10,2);
    declare coutPlatefrom DECIMAL(10,2);
    declare nbPersonnesEnrollee INT;

    declare messageErreur VARCHAR(100); 

    -- récupération du cout journalier de la plateforme 
    -- utilisé pour la nouvelle campagne
    SELECT coutJournalier into coutPlatefrom
    FROM PLATEFORME
    WHERE nomPlateforme = new.nomPlateforme;

    SELECT remainingBudget(new.dateDebut) into budgetRestant;

    -- vérification de la validité des couts de la campagne 
    if (new.duree * coutPlatefrom) > budgetRestant then
        set messageErreur = CONCAT('Coût dépassant du budget restant :  ',new.duree * coutPlatefrom,' coût de la plateforme    |   ',budgetRestant,'  budget restant.');
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;

    -- verification de validité d'utilisation de la plateforme 
    if not plateformeAvailable(new.dateDebut,new.nomPlateforme) then
        set messageErreur = 'La plateforme n''est pas disponible à cette date';
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;

    -- verification des maintenance de la plateforme
    if not plateformeInMaintenace(new.dateDebut,new.duree,new.nomPlateforme) then
       set messageErreur = 'La plateforme sera en maintenance ou est en maitenance au cours de la campagne';
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if; 
end |

create or replace TRIGGER checkUpadateUnEquipementSurPlateforme
before UPDATE ON INCLURE_EQUIPEMENT for each ROW
begin
    declare idEquipementP INT;
    declare nbEquipementP INT;
    declare messageErreur VARCHAR(100);

    -- récupère l'id de l'équipement et compte les occurrences
    SET idEquipementP = new.idEquipement;
    
    SELECT count(*) into nbEquipementP
    FROM INCLURE_EQUIPEMENT
    WHERE idEquipement = new.idEquipement
    AND (nomPlateforme != new.nomPlateforme OR idEquipement != old.idEquipement);

    -- vérifier que l'équipement ne soit pas déjà dans une autre plateforme
    if (nbEquipementP > 0) then
        set messageErreur = concat("L'équipement numéro : ", idEquipementP, " ne peut pas être dans plusieurs plateformes simultanément");
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;
end |

create or replace trigger checkChercheurParticipation
before INSERT on PARTICIPER_CAMPAGNE for each row
begin
    declare messageErreur VARCHAR(100);
    declare campagneStartDay DATE; 
    -- vérification de disponibilité de la personne 

    SELECT dateDebut into campagneStartDay
    FROM CAMPAGNE
    WHERE idCampagne = new.idCampagne;

    if exists (SELECT * FROM PARTICIPER_CAMPAGNE NATURAL JOIN CAMPAGNE WHERE idPersonnel = new.idPersonnel AND (DATE_ADD(dateDebut,INTERVAL duree DAY) > campagneStartDay AND valide)) then
        set messageErreur = 'Le chercheur est déja occupé sur une campagne au commencement de celle-ci';
        signal SQLSTATE '45000' SET MESSAGE_TEXT = messageErreur;
    end if;
end |

create or replace trigger checkCampagneValidity
after INSERT on PARTICIPER_CAMPAGNE for each ROW
begin

    declare nbPersonnesEnrollee INT;
    declare nbPersonnesRequired INT;
    declare habilitationSearched INT;
    declare fini BOOLEAN default false;
    -- on part du principe que les contitions sont vérifié
    declare isValide BOOLEAN default true;
    declare getHabilitationsRequired cursor for 
        SELECT idHabilitation
        FROM CAMPAGNE NATURAL JOIN INCLURE_EQUIPEMENT NATURAL JOIN NECESSITER_HABILITATION
        WHERE idCampagne = new.idCampagne;

    declare continue handler for not found set fini = true;

    -- verification de validité de la campagne (représentation des habilitations nécessaires et nb de personnes enrollées)

    open getHabilitationsRequired;
    while not fini do
        fetch getHabilitationsRequired into habilitationSearched;
        if not fini then
            SELECT verifyHabilitationValidity(new.idCampagne,habilitationSearched) into isValide;
            if not isValide then
            -- les conditions ne sont pas remplisent, on peut stopper la verification
                set fini = false;
            end if;
        end if;
    end while;
    close getHabilitationsRequired;

    SELECT distinct nbPersonnesRequises into nbPersonnesRequired
    FROM PARTICIPER_CAMPAGNE NATURAL JOIN CAMPAGNE NATURAL JOIN PLATEFORME
    WHERE idCampagne = new.idCampagne;

    SELECT COUNT(idPersonnel) INTO nbPersonnesEnrollee
    FROM PARTICIPER_CAMPAGNE
    WHERE idCampagne = new.idCampagne; 

    if (isValide AND nbPersonnesEnrollee >= nbPersonnesRequired) then 
        UPDATE CAMPAGNE 
        SET valide = true 
        WHERE idCampagne = new.idCampagne;
    end if;
end |

create or replace trigger checkCampagneValidityAfterDelete
after DELETE on PARTICIPER_CAMPAGNE for each ROW
begin

    declare nbPersonnesEnrollee INT;
    declare nbPersonnesRequired INT;
    declare habilitationSearched INT;
    declare fini BOOLEAN default false;
    -- on part du principe que les contitions sont vérifié
    declare isValide BOOLEAN default true;
    declare getHabilitationsRequired cursor for 
        SELECT idHabilitation
        FROM CAMPAGNE NATURAL JOIN INCLURE_EQUIPEMENT NATURAL JOIN NECESSITER_HABILITATION
        WHERE idCampagne = old.idCampagne;

    declare continue handler for not found set fini = true;

    -- verification de validité de la campagne (représentation des habilitations nécessaires et nb de personnes enrollées)

    open getHabilitationsRequired;
    while not fini do
        fetch getHabilitationsRequired into habilitationSearched;
        if not fini then
            SELECT verifyHabilitationValidity(old.idCampagne,habilitationSearched) into isValide;
            if not isValide then
            -- les conditions ne sont pas remplisent, on peut stopper la verification
                set fini = false;
            end if;
        end if;
    end while;
    close getHabilitationsRequired;

    SELECT distinct nbPersonnesRequises into nbPersonnesRequired
    FROM PARTICIPER_CAMPAGNE NATURAL JOIN CAMPAGNE NATURAL JOIN PLATEFORME
    WHERE idCampagne = old.idCampagne;

    SELECT COUNT(idPersonnel) INTO nbPersonnesEnrollee
    FROM PARTICIPER_CAMPAGNE
    WHERE idCampagne = old.idCampagne; 

    if NOT(isValide AND nbPersonnesEnrollee >= nbPersonnesRequired) then 
        UPDATE CAMPAGNE 
        SET valide = false 
        WHERE idCampagne = old.idCampagne;
    end if;
end |

-- Un équipement ne peut être utilisé par plusieurs plateformes simultanément.

create or replace TRIGGER checkUnEquipementSurPlateforme
before INSERT ON INCLURE_EQUIPEMENT for each ROW
begin
    declare idEquipementP INT;
    declare nbEquipementP INT;
    declare messageErreur VARCHAR(100);

    -- récupère l'id de l'équipement et compte les occurrences existantes
    SET idEquipementP = new.idEquipement;
    
    SELECT count(*) into nbEquipementP
    FROM INCLURE_EQUIPEMENT
    WHERE idEquipement = new.idEquipement;

    -- vérifier que l'équipement ne fasse pas déjà partie d'une plateforme
    if (nbEquipementP > 0) then
        set messageErreur = concat("L'équipement numéro : ", idEquipementP, " ne peut pas être dans plusieurs plateformes simultanément");
        signal SQLSTATE '45000' set MESSAGE_TEXT = messageErreur;
    end if;
end |

-- create or replace EVENT deleteInvalidCampaign ON SCHEDULE EVERY 1 MINUTE DO
--     call clearCampaign();
