# 🎮 Puissance 4 - Clone Web Complet

Clone web **PARFAIT et COMPLET** du jeu de Puissance 4 avec architecture Flask + Python + JavaScript.

## 🚀 Fonctionnalités

### ✅ 3 Modes de Jeu Disponibles

1. **Joueur vs Joueur (PvP)** 
   - Deux joueurs humains alternent les coups
   - Rouge 🔴 vs Jaune 🟡

2. **Joueur vs IA (PvAI)**
   - Le joueur (Rouge) affronte l'IA (Jaune)
   - Choix de difficulté : Facile (Aléatoire) ou Difficile (Minimax)

3. **IA vs IA (AIvsAI)**
   - Mode automatique spectateur
   - Deux IA s'affrontent en temps réel
   - Parfait pour tester les algorithmes

### 🎨 Interface Moderne

- Design épuré avec dégradé violet
- Plateau bleu 9×9 centré
- Animation de chute des jetons
- Surlignage des jetons gagnants (effet pulse)
- Messages de statut en temps réel

### 🤖 Intelligence Artificielle

- **IA Aléatoire** : Niveau facile, joue au hasard
- **IA Minimax** : Niveau difficile, algorithme avec élagage alpha-beta (profondeur 4)

## 📂 Architecture

```
deployFour/
├── app.py                  # 🔧 Backend Flask avec API REST
├── templates/
│   └── index.html          # 🎨 Frontend complet (HTML + CSS + JS)
├── requirements.txt        # 📦 Dépendances Python
└── README.md              # 📖 Ce fichier
```

### 🔌 Routes API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Interface de jeu |
| `/api/get_ai_move` | POST | Demande un coup à l'IA |
| `/api/check_win` | POST | Vérifie victoire/égalité |
| `/health` | GET | Status du serveur |

## 🛠️ Installation

### 1. Prérequis

- Python 3.10+
- Environnement virtuel (`.venv` à la racine de ConnectFour)

### 2. Installation des dépendances

Depuis le dossier `ConnectFour/deployFour/` :

```bash
# Avec l'environnement virtuel activé
pip install -r requirements.txt
```

Ou installation manuelle :

```bash
pip install Flask==3.0.2 gunicorn==21.2.0 numpy==1.26.2 Werkzeug==3.0.1
```

### 3. Vérifier la structure

Assurez-vous que la structure suivante existe :

```
ConnectFour/
├── src/                    # ✅ Code métier (models, ai, utils)
│   ├── models/
│   │   └── board.py
│   ├── ai/
│   │   ├── minimax_ai.py
│   │   └── random_ai.py
│   └── utils/
│       └── constants.py
└── deployFour/             # ✅ Application web
    ├── app.py
    └── templates/
        └── index.html
```

## 🎯 Lancement

### Développement (local)

```bash
# Depuis deployFour/
python app.py
```

Le serveur démarre sur : **http://localhost:5001**

> **Note** : Port 5001 utilisé car le port 5000 est souvent occupé par AirPlay Receiver sur macOS.

### Production (avec Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## 🎮 Utilisation

1. **Ouvrir le navigateur** : http://localhost:5001
2. **Choisir le mode de jeu** : PvP / PvAI / AIvsAI
3. **Sélectionner la difficulté IA** (si applicable)
4. **Cliquer sur "Nouvelle Partie"**
5. **Jouer !**
   - Mode PvP : Cliquez sur une colonne pour jouer
   - Mode PvAI : Jouez (Rouge), l'IA répond automatiquement (Jaune)
   - Mode AIvsAI : Regardez les deux IA s'affronter

## 🧪 Tests

### Test manuel rapide

1. Lancer le serveur
2. Ouvrir http://localhost:5001
3. Tester les 3 modes :
   - PvP : Jouez quelques coups manuellement
   - PvAI (Facile) : Jouez contre l'IA aléatoire
   - PvAI (Difficile) : Jouez contre Minimax
   - AIvsAI : Laissez les IA jouer seules

### Vérifier les routes API

```bash
# Health check
curl http://localhost:5001/health

# Test IA move (avec une grille vide)
curl -X POST http://localhost:5001/api/get_ai_move \
  -H "Content-Type: application/json" \
  -d '{"grid": [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]], "ai_type": "random", "player": 2}'
```

## 🐛 Dépannage

### Erreur "ModuleNotFoundError: No module named 'flask'"

```bash
# Vérifier l'environnement virtuel
which python3

# Activer le venv
source ../.venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Port déjà utilisé (Port 5000/5001 in use)

```bash
# Sur macOS, désactiver AirPlay Receiver
# Préférences Système → Général → AirDrop et Handoff

# Ou changer le port dans app.py
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Erreur d'import depuis `src/`

Vérifier que le chemin est correct dans `app.py` :

```python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

Cette ligne permet d'importer depuis `ConnectFour/src/` même si on est dans `ConnectFour/deployFour/`.

## 📊 Fonctionnalités Techniques

### Backend (Flask)

- **Import dynamique** : `sys.path.append` pour accéder aux modules `src/`
- **Réutilisation du code métier** : Board, MinimaxAI, RandomAI
- **Conversion d'indices** : Gestion de l'inversion Y entre JS (haut=0) et Python (bas=0)
- **Cache d'IA** : Instances réutilisées pour performances
- **Gestion d'erreurs** : Try/except avec logs détaillés

### Frontend (JavaScript)

- **Grille dynamique** : Génération en grid CSS (9×9)
- **État réactif** : Variables globales synchronisées
- **Animations CSS** : Chute des jetons + effet de victoire
- **Fetch API** : Requêtes asynchrones vers le backend
- **Mode spectateur** : Boucle automatique pour IA vs IA

### Convention d'Indices

| Contexte | Convention | Exemple |
|----------|-----------|---------|
| **JavaScript (Frontend)** | `grid[0]` = haut visuel | Ligne 0 = haut du plateau |
| **Python (Backend)** | `board.grid[0]` = bas physique | Ligne 0 = fond du plateau |
| **Conversion** | `row_display = ROWS - 1 - row_internal` | Inversion Y automatique |

## 📝 Changelog

### v1.0 (5 mars 2026)

✅ Backend Flask complet avec :
- Route `/api/get_ai_move` pour les coups d'IA
- Route `/api/check_win` pour détection de victoire
- Support de Minimax et Random AI
- Conversion d'indices automatique

✅ Frontend moderne avec :
- 3 modes de jeu (PvP, PvAI, AIvsAI)
- Interface responsive
- Animations fluides
- Surlignage ligne gagnante

✅ Documentation complète

## 🚀 Prochaines Améliorations Possibles

- [ ] Sauvegarde des parties en base de données
- [ ] Historique des parties jouées
- [ ] Mode replay pour revoir une partie
- [ ] Classement ELO entre IA
- [ ] Support multi-joueurs en réseau (WebSocket)
- [ ] Mode tournoi automatique
- [ ] Statistiques de victoire par joueur/IA
- [ ] Thèmes personnalisables

## 📄 Licence

Projet éducatif - Tous droits réservés

---

**Développé avec ❤️ en Python + Flask + JavaScript**

🎮 Bon jeu !
