"""Exceptions métier de l'application."""


class SalaireInvalideError(ValueError):
    """Signale un salaire nul ou négatif."""


class EmployeExistantError(ValueError):
    """Signale qu'un matricule est déjà utilisé."""
