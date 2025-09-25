
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
INSERT INTO CAMPAGNE VALUES (5,'Black Betty',CURDATE(),5,'Lailly-en-Val');

UPDATE BUDGET set budgetTotal = 500 WHERE dateMoisAnnee = CURDATE();
DELETE FROM CAMPAGNE;
DELETE FROM PLATEFORME;

-- INSERT INTO PLATEFORME VALUES ('Black Betty',5,50.99,30);

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