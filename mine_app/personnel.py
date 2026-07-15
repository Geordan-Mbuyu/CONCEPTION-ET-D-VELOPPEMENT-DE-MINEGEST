"""Modèle objet : employés, héritage, polymorphisme et décorateurs."""

import re
from abc import ABC, abstractmethod

from .exceptions import SalaireInvalideError


TAUX_HEURE_SUPP = 5.0


class Employe(ABC):
    """Classe abstraite qui encapsule les données communes d'un employé."""

    def __init__(self, matricule: str, nom: str, prenom: str, salaire: float) -> None:
        self.matricule = matricule
        self.nom = self._valider_nom(nom).upper()
        self.prenom = self._valider_nom(prenom).title()
        self.salaire_base = salaire

    @property
    def matricule(self) -> str:
        """Retourne le matricule."""
        return self.__matricule

    @matricule.setter
    def matricule(self, valeur: str) -> None:
        valeur = valeur.strip().upper()
        if not re.fullmatch(r"[A-Z]\d{3}", valeur):
            raise ValueError("Le matricule doit être une lettre suivie de trois chiffres (M001).")
        self.__matricule = valeur

    @staticmethod
    def _valider_nom(valeur: str) -> str:
        """Vérifie qu'un nom contient uniquement des lettres."""
        valeur = valeur.strip()
        if not valeur or not all(mot.isalpha() for mot in valeur.split()):
            raise ValueError("Le nom et le prénom doivent contenir uniquement des lettres.")
        return valeur

    @property
    def salaire_base(self) -> float:
        """Retourne le salaire de base."""
        return self.__salaire_base

    @salaire_base.setter
    def salaire_base(self, valeur: float) -> None:
        valeur = float(valeur)
        if valeur <= 0:
            raise SalaireInvalideError("Le salaire doit être strictement positif.")
        self.__salaire_base = valeur

    @abstractmethod
    def calculer_salaire(self) -> float:
        """Calcule le salaire mensuel."""

    @abstractmethod
    def obtenir_fonction(self) -> str:
        """Retourne la fonction de l'employé."""


class EmployeTerrain(Employe, ABC):
    """Deuxième niveau d'héritage pour les métiers de terrain."""

    TAUX_PRIME = 0.0

    def __init__(self, matricule: str, nom: str, prenom: str, salaire: float) -> None:
        super().__init__(matricule, nom, prenom, salaire)

    def calculer_salaire(self) -> float:
        """Ajoute la prime du métier au salaire de base."""
        return self.salaire_base * (1 + self.TAUX_PRIME)


class Mineur(EmployeTerrain):
    """Troisième niveau d'héritage : mineur."""

    TAUX_PRIME = 0.20

    def obtenir_fonction(self) -> str:
        """Retourne le métier."""
        return "Mineur"


class Superviseur(EmployeTerrain):
    """Troisième niveau d'héritage : superviseur."""

    TAUX_PRIME = 0.15

    def obtenir_fonction(self) -> str:
        """Retourne le métier."""
        return "Superviseur"


class EmployeBureau(Employe):
    """Deuxième niveau d'héritage pour les métiers administratifs."""

    TAUX_PRIME = 0.05

    def calculer_salaire(self) -> float:
        """Ajoute une prime administrative de 5 %."""
        return self.salaire_base * (1 + self.TAUX_PRIME)

    def obtenir_fonction(self) -> str:
        """Retourne le métier."""
        return "Employé de bureau"


class Comptable(EmployeBureau):
    """Troisième niveau d'héritage : comptable."""

    def obtenir_fonction(self) -> str:
        """Surcharge la fonction administrative générale."""
        return "Comptable"


class EmployeDecorator:
    """Classe de base qui conserve l'employé à décorer."""

    def __init__(self, employe) -> None:
        self._employe = employe


class PrimeNuit(EmployeDecorator):
    """Ajoute une prime de nuit fixe."""

    def __init__(self, employe, montant: float) -> None:
        super().__init__(employe)
        self.montant = float(montant)
        if self.montant < 0:
            raise ValueError("La prime de nuit ne peut pas être négative.")

    def calculer_salaire(self) -> float:
        """Décore le calcul du salaire."""
        return self._employe.calculer_salaire() + self.montant


class PrimeHeuresSupplementaires(EmployeDecorator):
    """Ajoute le paiement des heures supplémentaires."""

    def __init__(self, employe, heures: float) -> None:
        super().__init__(employe)
        self.heures = float(heures)
        if self.heures < 0:
            raise ValueError("Les heures supplémentaires doivent être positives.")

    def calculer_salaire(self) -> float:
        """Décore le calcul du salaire."""
        return self._employe.calculer_salaire() + self.heures * TAUX_HEURE_SUPP


TYPES_EMPLOYES = {"Mineur": Mineur, "Superviseur": Superviseur, "Comptable": Comptable}


def calculer_paie(objet) -> float:
    """Exemple de duck typing : seule la méthode de l'objet compte."""
    return objet.calculer_salaire()


def creer_employe(fonction: str, *donnees) -> Employe:
    """Fabrique un employé selon sa fonction."""
    try:
        return TYPES_EMPLOYES[fonction](*donnees)
    except KeyError as erreur:
        raise ValueError(f"Fonction inconnue : {fonction}") from erreur
