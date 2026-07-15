"""Service métier unique de gestion de la mine."""

from pathlib import Path

from .personnel import PrimeHeuresSupplementaires, PrimeNuit, calculer_paie, creer_employe
from .stockage import RegistreEmployes


class GestionMine:
    """Singleton coordonnant le modèle et la persistance."""

    _instance = None

    def __new__(cls, chemin_db: str | Path = "mine.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialise = False
        return cls._instance

    def __init__(self, chemin_db: str | Path = "mine.db") -> None:
        if not self._initialise:
            self.registre = RegistreEmployes(chemin_db)
            self._initialise = True

    def ajouter_employe(
        self, fonction: str, matricule: str, nom: str, prenom: str, salaire: float
    ) -> None:
        """Valide puis enregistre un nouvel employé."""
        self.registre.ajouter(creer_employe(fonction, matricule, nom, prenom, salaire))

    def supprimer_employe(self, matricule: str) -> None:
        """Supprime un employé à partir de son matricule."""
        self.registre.supprimer(matricule)

    def attribuer_primes(self, matricule: str, nuit: float, heures: float) -> None:
        """Valide et enregistre les primes d'un employé."""
        if min(nuit, heures) < 0:
            raise ValueError("Les valeurs de primes ne peuvent pas être négatives.")
        self.registre.definir_primes(matricule, nuit, heures)

    def lister_employes(self) -> list[dict]:
        """Retourne les employés avec leur salaire polymorphe."""
        resultat = []
        for ligne in self.registre.lister():
            try:
                employe = self.registre.convertir(ligne)
                if ligne["prime_nuit"]:
                    employe = PrimeNuit(employe, ligne["prime_nuit"])
                if ligne["heures_supp"]:
                    employe = PrimeHeuresSupplementaires(employe, ligne["heures_supp"])
                # Duck typing : employe peut être un Employe ou un décorateur.
                ligne["salaire_total"] = calculer_paie(employe)
                ligne["prime_total"] = ligne["salaire_total"] - ligne["salaire_base"]
                ligne["erreur"] = ""
            except ValueError as erreur:
                # Une ancienne donnée invalide ne doit jamais arrêter l'application.
                ligne["salaire_total"] = 0.0
                ligne["prime_total"] = 0.0
                ligne["erreur"] = str(erreur)
            resultat.append(ligne)
        return resultat

    def statistiques(self) -> tuple[int, float]:
        """Retourne l'effectif et la masse salariale."""
        employes = self.lister_employes()
        return len(employes), sum(item["salaire_total"] for item in employes)
