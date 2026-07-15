"""Point d'entrée de l'application de gestion minière."""

from mine_app.interface import MineApplication


def main() -> None:
    """Démarre l'interface graphique."""
    app = MineApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
