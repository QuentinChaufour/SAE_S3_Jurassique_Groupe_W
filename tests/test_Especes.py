from exploitation_echantillons.espece_averee import EspeceAveree
from exploitation_echantillons.espece import EspeceHypothetique

def test_espece_avere():
    """Méthode de test d'une Espece averée"""

    lion :EspeceAveree = EspeceAveree("lion","Panthera leo","AATCGGTCA")
    assert(lion.get_genome() == "AATCGGTCA")
    lion.set_genome("AATCGGTCATTGCA")
    assert(lion.get_genome() == "AATCGGTCATTGCA")
    assert(lion.get_nom() == "lion")
    assert(lion.get_nom_sci() == "Panthera leo")
    chat :EspeceAveree = EspeceAveree("chat domestique", "Felis catus", "GATCCGTCA")
    lion.add(chat)

    assert(chat in lion.get_enfants())

def test_espece_hypothetique():
    """Méthode de test d'une Espece hypothetique"""
    placentalia: EspeceHypothetique = EspeceHypothetique("Placentaire","Placentalia")

    atlantogenata: EspeceHypothetique = EspeceHypothetique("Atlantogenata", "Atlantogenata")
    boreoeutheria: EspeceHypothetique = EspeceHypothetique("Boréoeuthériens", "Boreoeutheria")

    placentalia.add_enfants(atlantogenata)
    placentalia.add_enfants(boreoeutheria)

    assert(placentalia.get_nom() == "Placentaire")
    assert(placentalia.get_nom_sci() == "Placentalia")
    assert(boreoeutheria in placentalia.get_enfants())

    representation: str = "└── L'espèce hypothétique Placentaire (Placentalia)\n    ├── L'espèce hypothétique Atlantogenata (Atlantogenata)\n    └── L'espèce hypothétique Boréoeuthériens (Boreoeutheria)"

    assert(str(placentalia) == representation)

    placentalia.remove_enfant(boreoeutheria)
    assert(boreoeutheria not in placentalia.get_enfants())

    placentalia.set_nom("Nouveau nom")
    assert(placentalia.get_nom() == "Nouveau nom")
    placentalia.set_nom_sci("Nouveau nom sci")
    assert(placentalia.get_nom_sci() == "Nouveau nom sci")
    