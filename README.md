# MineGest

MineGest est une application pédagogique de gestion des employés et des primes
d'une entreprise minière. Elle illustre l'encapsulation, l'abstraction,
l'héritage sur trois niveaux, le polymorphisme et les patterns Singleton et
Decorator.

## Prérequis

- Python 3.10 ou plus récent
- Tkinter (inclus dans l'installation standard de Python sous Windows)

Le projet n'utilise aucune bibliothèque externe.

## Lancement

Depuis le dossier `gestion_mine` :

```powershell
python main.py
```

La base `mine.db` est créée automatiquement au premier lancement.

## Livrables

- [Rapport technique final](rapport/Rapport_technique_MineGest_final.docx)
- [Présentation MineGest](presentation/Presentation_MineGest.pptx)
- Captures de l'interface dans le dossier `captures/`

## Tests

Depuis le dossier `gestion_mine` :

```powershell
python -m unittest discover -s tests -v
```

Les cinq tests couvrent l'identité de l'employé, le polymorphisme, les
décorateurs, la validation du salaire, les doublons SQLite et le Singleton.

## Utilisation

1. Ouvrir la vue **Employés** et enregistrer un mineur, un superviseur ou un comptable.
   Le matricule contient une lettre et trois chiffres (`M001`) ; le nom et le prénom
   acceptent uniquement des lettres.
2. Ouvrir la vue **Primes** pour attribuer une prime de nuit ou des heures
   supplémentaires. Le taux des heures supplémentaires est fixé à **5 $/h**.
3. Consulter le salaire de base, les primes et le salaire total dans la vue
   **Employés**, puis la masse salariale depuis le tableau de bord.

## Organisation

```text
gestion_mine/
├── main.py
├── mine_app/
│   ├── stockage.py     # persistance SQLite
│   ├── exceptions.py   # exceptions personnalisées
│   ├── interface.py    # trois vues Tkinter
│   ├── personnel.py    # classes métier et Decorator
│   └── gestion.py      # Singleton GestionMine
├── tests/              # cinq tests automatiques
├── captures/           # captures de l'interface
├── presentation/       # support PowerPoint
└── rapport/            # rapport technique
```

## Concepts de POO

- **Encapsulation** : attributs privés et propriétés validées dans `Employe`.
- **Abstraction** : `Employe` et `EmployeTerrain` sont abstraites.
- **Héritage** : `Employe -> EmployeTerrain -> Mineur/Superviseur`.
- **Polymorphisme** : chaque fonction redéfinit le calcul ou l'identité métier ;
  `calculer_paie` illustre le duck typing sans vérifier la classe de l'objet.
- **Singleton** : une seule instance de `GestionMine`.
- **Decorator** : `PrimeNuit` et `PrimeHeuresSupplementaires` combinables.
- **Exceptions** : `SalaireInvalideError` et `EmployeExistantError`.
- **Persistance** : `RegistreEmployes` enregistre les données dans SQLite.
