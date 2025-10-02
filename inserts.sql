
delimiter |
create or replace procedure clear_all()
begin
    DELETE FROM ECHANTILLON;
    DELETE FROM ESPECE;
    DELETE FROM PARTICIPER_CAMPAGNE;
    DELETE FROM POSSEDER_HABILITATION;
    DELETE FROM INCLURE_EQUIPEMENT;
    DELETE FROM NECESSITER_HABILITATION;
    DELETE FROM HABILITATION;
    DELETE FROM EQUIPEMENT;
    DELETE FROM MAINTENANCE;
    DELETE FROM PERSONNEL;
    DELETE FROM CAMPAGNE;
    DELETE FROM PLATEFORME;
    DELETE FROM BUDGET;
end |

delimiter ;

    ---------------------------------------------
    -- vérifications des contraintes du Budget --
    ---------------------------------------------

INSERT INTO BUDGET VALUES ('2025-01-01', 1000.00);
INSERT INTO BUDGET VALUES ('2025-02-01', 1500.00);
INSERT INTO BUDGET VALUES ('2025-03-01', 2000.00);
INSERT INTO BUDGET VALUES (CURDATE(), 2500.00);
UPDATE BUDGET set budgetTotal = 4000 WHERE dateMoisAnnee = CURDATE();

-- > erreur d'insertion : budget négatif
INSERT INTO BUDGET VALUES ('2025-05-01', -500.00);

-- > erreur d'insertion : budget déjà existant pour le mois et l'année
INSERT INTO BUDGET VALUES ('2025-01-15', 1200.00);

-- > erreur d'update car le budget est négatif
UPDATE BUDGET set budgetTotal = -1000 WHERE dateMoisAnnee = '2025-09-01';

--> erreur d'update car date du budget déja dépassé
UPDATE BUDGET set budgetTotal = 4000 WHERE dateMoisAnnee = '2025-03-01';

-- > erreur d'update car le nouveau budget ne couvre pas les fonds engagé
INSERT INTO PLATEFORME VALUES ('Black Betty',5,200,30);
INSERT INTO CAMPAGNE VALUES (1,'Black Betty',CURDATE(),5,'Lailly-en-Val',true);

UPDATE BUDGET set budgetTotal = 500 WHERE dateMoisAnnee = CURDATE();

-- > erreur de delete car budget utilisé
DELETE FROM BUDGET where dateMoisAnnee = CURDATE();

call clear_all;

  -----------------------------------------------------
  -- verification des contraintes Inclure Equipement --
  -----------------------------------------------------

--> erreur d'insert et d'update car il y a un équipement 
-- insert
INSERT INTO EQUIPEMENT VALUES (012, "Pinceau");
INSERT INTO PLATEFORME VALUES ('Black Betty',5,50.99,30);
INSERT INTO PLATEFORME VALUES ('Black Pearl',5,50.99,30);
INSERT INCLURE_EQUIPEMENT VALUES('Black Betty', 012);
INSERT INCLURE_EQUIPEMENT VALUES('Black Pearl', 012);

--update
INSERT INTO EQUIPEMENT VALUES(013, "Pelle");
INSERT INCLURE_EQUIPEMENT VALUES('Black Pearl', 013);
UPDATE INCLURE_EQUIPEMENT set idEquipement = 012 WHERE nomPlateforme = 'Black Pearl';

call clear_all;

    -------------------------------------------
    -- vérification des contraintes Campagne -- 
    -------------------------------------------

INSERT INTO BUDGET VALUES (CURDATE(),5000);
INSERT INTO PLATEFORME VALUES ('Black Betty',5,200,30);
INSERT INTO CAMPAGNE VALUES (3,'Black Betty',CURDATE(),5,'Lailly-en-Val',true);

-- > erreur d'insert car Plateforme utilisé/occupé 
INSERT INTO CAMPAGNE VALUES (4,'Black Betty',DATE_ADD(CURDATE(), INTERVAL 1 DAY),5,'Chambord',true);

-- > erreur d'insert car fonds insuffisant
INSERT INTO CAMPAGNE VALUES (5,'Black Betty',DATE_ADD(CURDATE(), INTERVAL 10 DAY),25,'Chambord',true);

call clear_all;

    ----------------------------------------------------------
    -- vérification des contraintes Participation Chercheur --
    ----------------------------------------------------------

INSERT INTO BUDGET values (CURDATE(),5000);
INSERT INTO BUDGET values (DATE_ADD(CURDATE(), INTERVAL 1 MONTH),5000);
INSERT INTO PLATEFORME VALUES ('Black Betty',5,200,30);
INSERT INTO PLATEFORME VALUES ('Black Bolt',2,300,30);
INSERT INTO CAMPAGNE VALUES (1,'Black Betty',CURDATE(),5 ,'Lailly-en-Val',true);
INSERT INTO PERSONNEL VALUES (1,'Olivier', 'éboué', 'azertyuiop', 'chercheur');

INSERT INTO PARTICIPER_CAMPAGNE values (1,1);
INSERT INTO CAMPAGNE VALUES (2,'Black Bolt',DATE_ADD(CURDATE(), INTERVAL 2 DAY),2,'Chambord',true);

-- > erreur d'insert car le chercheur participe déja a la campagne à Lailly-en-val
INSERT INTO PARTICIPER_CAMPAGNE values (1,2);

INSERT INTO PERSONNEL VALUES (2,'Jack', 'kun', 'qsdfghjklm', 'chercheur');
INSERT INTO CAMPAGNE VALUES (3,'Black Bolt',DATE_ADD(CURDATE(), INTERVAL 10 DAY),2,'Chambord',false);

INSERT INTO PARTICIPER_CAMPAGNE values (1,3);
INSERT INTO PARTICIPER_CAMPAGNE values (2,3);

-- > campagne valide car nb personnel requis vérifié et pas d'habilitations nécesaire
SELECT valide FROM CAMPAGNE where idCampagne = 3; --> true
DELETE FROM PARTICIPER_CAMPAGNE WHERE idCampagne = 3 AND idPersonnel = 2;
SELECT valide FROM CAMPAGNE where idCampagne = 3; --> false

call clear_all;