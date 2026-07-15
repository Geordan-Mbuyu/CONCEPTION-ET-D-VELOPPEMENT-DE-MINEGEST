"""Tests unitaires des principaux comportements de MineGest."""

import tempfile
import unittest
from pathlib import Path

from mine_app.exceptions import EmployeExistantError, SalaireInvalideError
from mine_app.gestion import GestionMine
from mine_app.personnel import (
    Mineur,
    PrimeHeuresSupplementaires,
    PrimeNuit,
    Superviseur,
    calculer_paie,
)
from mine_app.stockage import RegistreEmployes


class MineGestTests(unittest.TestCase):
    """Vérifie le modèle objet, les patterns et la persistance."""

    def setUp(self) -> None:
        GestionMine._instance = None
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_mine.db"

    def tearDown(self) -> None:
        GestionMine._instance = None
        self.temp_dir.cleanup()

    def test_matricule_et_identite(self) -> None:
        employe = Mineur("m001", "kabeya", "jean", 1000)

        self.assertEqual(employe.matricule, "M001")
        self.assertEqual(employe.nom, "KABEYA")
        self.assertEqual(employe.prenom, "Jean")

    def test_polymorphisme_et_decorateurs(self) -> None:
        mineur = Mineur("M001", "Kabeya", "Jean", 1000)
        superviseur = Superviseur("S001", "Ilunga", "Paul", 1000)

        self.assertEqual(calculer_paie(mineur), 1200)
        self.assertEqual(calculer_paie(superviseur), 1150)

        salaire_decore = PrimeHeuresSupplementaires(
            PrimeNuit(mineur, 50), 10
        )
        self.assertEqual(calculer_paie(salaire_decore), 1300)

    def test_salaire_invalide(self) -> None:
        with self.assertRaises(SalaireInvalideError):
            Mineur("M001", "Kabeya", "Jean", 0)

    def test_doublon(self) -> None:
        registre = RegistreEmployes(self.db_path)
        registre.ajouter(Mineur("M001", "Kabeya", "Jean", 1000))

        with self.assertRaises(EmployeExistantError):
            registre.ajouter(Mineur("M001", "Ilunga", "Paul", 1200))

    def test_singleton(self) -> None:
        premier = GestionMine(self.db_path)
        second = GestionMine(self.db_path)

        self.assertIs(premier, second)


if __name__ == "__main__":
    unittest.main()

