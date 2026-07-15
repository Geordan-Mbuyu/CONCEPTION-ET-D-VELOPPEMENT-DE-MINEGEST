"""Sauvegarde des employés dans une base SQLite."""

import sqlite3
from contextlib import contextmanager

from .exceptions import EmployeExistantError
from .personnel import creer_employe


class RegistreEmployes:
    """Gère les opérations sur la table des employés."""

    def __init__(self, chemin="mine.db"):
        self.chemin = str(chemin)
        self._initialiser()

    @contextmanager
    def _connexion(self):
        """Ouvre, valide et ferme automatiquement une connexion."""
        connexion = sqlite3.connect(self.chemin)
        connexion.row_factory = sqlite3.Row
        try:
            yield connexion
        except Exception:
            connexion.rollback()
            raise
        else:
            connexion.commit()
        finally:
            connexion.close()

    def _initialiser(self):
        """Crée la table si elle n'existe pas encore."""
        with self._connexion() as connexion:
            connexion.execute("""
                CREATE TABLE IF NOT EXISTS employes (
                    matricule TEXT PRIMARY KEY,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    fonction TEXT NOT NULL,
                    salaire_base REAL NOT NULL CHECK (salaire_base > 0),
                    prime_nuit REAL NOT NULL DEFAULT 0,
                    heures_supp REAL NOT NULL DEFAULT 0
                )
            """)

    def ajouter(self, employe):
        """Ajoute un employé dans la base."""
        try:
            with self._connexion() as connexion:
                connexion.execute(
                    """INSERT INTO employes
                       (matricule, nom, prenom, fonction, salaire_base)
                       VALUES (?, ?, ?, ?, ?)""",
                    (employe.matricule, employe.nom, employe.prenom,
                     employe.obtenir_fonction(), employe.salaire_base),
                )
        except sqlite3.IntegrityError as erreur:
            raise EmployeExistantError(
                f"Le matricule {employe.matricule} existe déjà."
            ) from erreur

    def supprimer(self, matricule):
        """Supprime un employé."""
        with self._connexion() as connexion:
            connexion.execute("DELETE FROM employes WHERE matricule=?", (matricule,))

    def definir_primes(self, matricule, nuit, heures):
        """Modifie les primes d'un employé."""
        with self._connexion() as connexion:
            connexion.execute(
                """UPDATE employes SET prime_nuit=?, heures_supp=?
                   WHERE matricule=?""",
                (nuit, heures, matricule),
            )

    def lister(self):
        """Retourne tous les employés."""
        with self._connexion() as connexion:
            lignes = connexion.execute("SELECT * FROM employes ORDER BY nom").fetchall()
        return [dict(ligne) for ligne in lignes]

    @staticmethod
    def convertir(ligne):
        """Transforme une ligne SQLite en objet Employe."""
        return creer_employe(
            ligne["fonction"], ligne["matricule"], ligne["nom"],
            ligne["prenom"], ligne["salaire_base"],
        )
