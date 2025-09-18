
### <ins>Modèle entité-association

> ![mcd](/MCD.svg)

Nous avons utilisé le site [Mocodo](https://www.mocodo.net/) pour produire ce modèle.

### <ins>Modèle relationnel

### <ins>Contraintes

#### Dépendances fonctionnelles

#### Autres dépendances 

- Dans une campagne, toutes les habilitations nécessaires doivent être représentés au sein des chercheurs participants a la campagne.
-  Le coût d'une campagne ne doit pas excéder le budget restant du mois du démarage de celle-ci.
- Une plateforme n'est pas en cours de maintenance lors du démarage d'une campagne.
- La plateforme utilisé durant une campagne ne doit pas avoir besoin de maintenance au cours de celle ci (la durée de la campagne ne fait pas dépasser l'intevalle de maintenance).
- Lors d'une campagne, les personnes et la plateforme ne doivent pas être occupé par une autre campagne simultanément.
