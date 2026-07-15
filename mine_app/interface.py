"""Interface Tkinter composée de trois vues."""

from pathlib import Path
from tkinter import Tk, messagebox, ttk

from .gestion import GestionMine


class MineApplication(Tk):
    """Fenêtre principale de MineGest."""

    def __init__(self):
        super().__init__()
        self.title("MineGest - Gestion des employés")
        self.geometry("850x600")
        self.service = GestionMine(Path(__file__).parents[1] / "mine.db")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f4f6f7")
        style.configure("TLabel", background="#f4f6f7", font=("Segoe UI", 10))
        style.configure("TButton", padding=6)
        style.configure("Treeview", rowheight=26)

        barre = ttk.Frame(self, padding=10)
        barre.pack(fill="x")
        ttk.Label(barre, text="MINEGEST", font=("Segoe UI", 18, "bold")).pack(side="left")
        for texte, commande in (
            ("Accueil", self.afficher_accueil),
            ("Employés", self.afficher_employes),
            ("Primes", self.afficher_primes),
        ):
            ttk.Button(barre, text=texte, command=commande).pack(side="left", padx=8)

        self.contenu = ttk.Frame(self, padding=20)
        self.contenu.pack(fill="both", expand=True)
        self.afficher_accueil()

    def _nouvelle_vue(self, titre):
        """Efface la vue précédente et affiche un nouveau titre."""
        for composant in self.contenu.winfo_children():
            composant.destroy()
        ttk.Label(self.contenu, text=titre, font=("Segoe UI", 20, "bold")).pack(anchor="w")

    @staticmethod
    def _champ(parent, texte, ligne, colonne):
        """Ajoute un champ de formulaire et retourne sa zone de saisie."""
        ttk.Label(parent, text=texte).grid(row=ligne, column=colonne, sticky="w", padx=5)
        entree = ttk.Entry(parent, width=22)
        entree.grid(row=ligne + 1, column=colonne, padx=5, pady=5)
        return entree

    def afficher_accueil(self):
        """Affiche la première vue : le tableau de bord."""
        self._nouvelle_vue("Tableau de bord")
        total, masse = self.service.statistiques()
        texte = f"{total} employé(s)\nMasse salariale : {masse:,.2f} $"
        ttk.Label(self.contenu, text=texte, font=("Segoe UI", 14)).pack(anchor="w", pady=30)

    def afficher_employes(self):
        """Affiche la deuxième vue : la gestion des employés."""
        self._nouvelle_vue("Gestion des employés")
        formulaire = ttk.Frame(self.contenu)
        formulaire.pack(fill="x", pady=15)

        champs = {
            "matricule": self._champ(formulaire, "Matricule", 0, 0),
            "nom": self._champ(formulaire, "Nom", 0, 1),
            "prenom": self._champ(formulaire, "Prénom", 0, 2),
            "salaire": self._champ(formulaire, "Salaire", 2, 0),
        }
        ttk.Label(formulaire, text="Fonction").grid(row=2, column=1, sticky="w")
        fonction = ttk.Combobox(formulaire, values=("Mineur", "Superviseur", "Comptable"),
                                state="readonly")
        fonction.set("Mineur")
        fonction.grid(row=3, column=1)
        ttk.Button(formulaire, text="Ajouter",
                   command=lambda: self._ajouter(champs, fonction.get())).grid(row=3, column=2)

        table = self._table_employes()
        table.pack(fill="both", expand=True, pady=10)
        ttk.Button(self.contenu, text="Supprimer la sélection",
                   command=lambda: self._supprimer(table)).pack(anchor="e")

    def _table_employes(self):
        """Crée et remplit le tableau des employés."""
        colonnes = ("matricule", "nom", "prenom", "fonction", "base", "primes", "total")
        table = ttk.Treeview(self.contenu, columns=colonnes, show="headings")
        titres = ("Matricule", "Nom", "Prénom", "Fonction", "Salaire", "Primes", "Total")
        for colonne, titre in zip(colonnes, titres):
            table.heading(colonne, text=titre)
            table.column(colonne, anchor="center", width=105)
        for employe in self.service.lister_employes():
            table.insert("", "end", values=(
                employe["matricule"], employe["nom"], employe["prenom"], employe["fonction"],
                f'{employe["salaire_base"]:.2f}', f'{employe["prime_total"]:.2f}',
                f'{employe["salaire_total"]:.2f}',
            ))
        return table

    def _ajouter(self, champs, fonction):
        """Enregistre les données du formulaire."""
        try:
            self.service.ajouter_employe(
                fonction, champs["matricule"].get(), champs["nom"].get(),
                champs["prenom"].get(), float(champs["salaire"].get()),
            )
        except ValueError as erreur:
            messagebox.showerror("Saisie invalide", str(erreur))
        else:
            messagebox.showinfo("Succès", "L'employé a été enregistré.")
            self.afficher_employes()

    def _supprimer(self, table):
        """Supprime l'employé sélectionné."""
        selection = table.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Sélectionnez un employé.")
            return
        matricule = table.item(selection[0], "values")[0]
        if messagebox.askyesno("Confirmation", f"Supprimer l'employé {matricule} ?"):
            self.service.supprimer_employe(matricule)
            self.afficher_employes()

    def afficher_primes(self):
        """Affiche la troisième vue : l'attribution des primes."""
        self._nouvelle_vue("Attribution des primes")
        employes = self.service.lister_employes()
        if not employes:
            ttk.Label(self.contenu, text="Ajoutez d'abord un employé.").pack(pady=30)
            return

        formulaire = ttk.Frame(self.contenu)
        formulaire.pack(anchor="w", pady=25)
        choix = [f'{e["matricule"]} - {e["nom"]} {e["prenom"]}' for e in employes]
        selection = ttk.Combobox(formulaire, values=choix, state="readonly", width=30)
        selection.set(choix[0])
        ttk.Label(formulaire, text="Employé").grid(row=0, column=0, sticky="w")
        selection.grid(row=0, column=1, padx=10)

        entrees = {}
        for ligne, (cle, texte) in enumerate((
            ("nuit", "Prime de nuit"),
            ("heures", "Heures supplémentaires (5 $/h)"),
        ), start=1):
            ttk.Label(formulaire, text=texte).grid(row=ligne, column=0, sticky="w")
            entrees[cle] = ttk.Entry(formulaire)
            entrees[cle].insert(0, "0")
            entrees[cle].grid(row=ligne, column=1, padx=10, pady=5)

        ttk.Button(formulaire, text="Enregistrer les primes",
                   command=lambda: self._enregistrer_primes(selection, entrees)).grid(
                       row=3, column=1, pady=10)

    def _enregistrer_primes(self, selection, entrees):
        """Enregistre les primes du formulaire."""
        try:
            matricule = selection.get().split(" - ", 1)[0]
            self.service.attribuer_primes(
                matricule, float(entrees["nuit"].get()), float(entrees["heures"].get()),
            )
        except ValueError as erreur:
            messagebox.showerror("Saisie invalide", str(erreur))
        else:
            messagebox.showinfo("Succès", "Les primes ont été enregistrées.")
            self.afficher_accueil()
