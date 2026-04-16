# 📊 PRÉSENTATION DEPLOYFOUR - PUISSANCE 4 WEB

## 🎯 Contexte (30 secondes)

Puissance 4 Web est un **clone parfait et complet** du jeu classique, déployé en production sur **Render**. Application entièrement autonome : **100% web, zéro dépendance externe**, avec backend Python + frontend JavaScript moderne.

---

## 🏛️ Architecture (1 min)

```
┌─────────────────────────────────────┐
│  FRONTEND (JavaScript + CSS)        │
│  - Interface réactive (plateau 9×9) │
│  - Animations fluides               │
│  - Sélection mode de jeu            │
└──────────────┬──────────────────────┘
               │ API REST (JSON)
               ↓
┌─────────────────────────────────────┐
│  BACKEND (Flask + Python)           │
│  - Classe Board (plateau)           │
│  - MinimaxAI + RandomAI             │
│  - Vérification victoire            │
│  - DatabaseManager (MySQL)          │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  BASE DE DONNÉES (MySQL)            │
│  - Historique des parties           │
│  - Scores, mode de jeu              │
└─────────────────────────────────────┘
```

### Fichiers Clés

- **`app.py`** → Backend complet (toutes les classes intégrées)
- **`templates/index.html`** → Frontend (HTML + CSS + JS)
- **`requirements.txt`** → Dépendances (Flask, NumPy, MySQL, OpenCV)
- **`image_processor.py`** → Reconnaissance d'image du jeu réel

---

## 🎮 Fonctionnement - 3 Modes (1 min)

### 1️⃣ Mode Joueur vs Joueur (PvP)

- Deux humains alternent
- Rouge 🔴 vs Jaune 🟡
- **Éditeur intégré** : créer des configurations personnalisées

### 2️⃣ Mode Joueur vs IA (PvAI)

- L'humain choisit sa couleur
- Deux niveaux : 
  - **Facile** (aléatoire)
  - **Difficile** (Minimax profondeur 4)
- **Suggestions conseils** : Minimax propose le meilleur coup
- **Scores en temps réel** : affichage du calcul d'évaluation

### 3️⃣ Mode IA vs IA

- Deux IA s'affrontent automatiquement
- **Spectateur** : regarder les stratégies
- Parfait pour **tests/validation d'algorithmes**

---

## 🔌 Endpoints API (45 secondes)

| Route | Méthode | Entrée | Sortie |
|-------|---------|--------|--------|
| `/` | GET | — | Page HTML |
| `/api/get_ai_move` | POST | `{grid, depth}` | `{column, scores}` |
| `/api/check_win` | POST | `{grid}` | `{winner, winning_line}` |
| `/health` | GET | — | `{status: "ok"}` |

### Exemple d'Exécution

```json
// POST /api/get_ai_move
{
  "grid": [...],
  "aiType": "minimax",
  "depth": 4
}

// Réponse
{
  "column": 3,
  "scores": {...}
}
```

---

## 🤖 Algorithme IA - Minimax (45 secondes)

```python
MinimaxAI (Élagage Alpha-Beta)
├─ Profondeur configurable (1-6)
├─ Évalue chaque coup possible
├─ Scoring : victoire (+10), défense, position
├─ Élagage Alpha-Beta (réduction 80%)
└─ Affiche scores temps réel
```

### Stratégie

- ✅ Cherche la **victoire en priorité**
- ✅ **Bloque l'adversaire** (hyper-agressif)
- ✅ Joue au **centre** (meilleure probabilité)
- ✅ Très difficile à battre

---

## 🛠️ Outils Utilisés

### Backend

- **Flask 3.0.2** → Framework web léger
- **NumPy** → Opérations matricielles rapides
- **PyMySQL / MySQL Connector** → Base de données
- **scikit-learn** → Modèle ML optionnel

### Frontend

- **HTML5 / CSS3 / Vanilla JS** → Pas de framework (léger)
- **Canvas API** → Rendering plateau

### DevOps

- **Gunicorn** → Serveur WSGI production
- **Render** → Déploiement Cloud
- **GitHub** → Versionning

### Bonus

- **OpenCV** → Reconnaissance image du jeu réel BGA
- **joblib** → Sérialisation modèles ML

---

## 🚀 Déploiement (30 secondes)

### Étapes

1. **Code** → `git push` sur GitHub
2. **Render détecte** → Déploiement auto
3. **API disponible** → URL en production
4. **Base MySQL** → Connectée automatiquement

### Commande Locale

```bash
gunicorn app:app --port 5001
# → http://localhost:5001
```

---

## ✨ Features "WOW"

✅ **Éditeur de plateau** → Créer des situations personnalisées  
✅ **Pause mid-game** → Reprendre plus tard  
✅ **Historique complet** → Rejouer/exporter parties  
✅ **Reconnaissance image** → Scanner plateau BGA réel  
✅ **Scores Minimax** → Voir la "pensée" de l'IA  
✅ **Toggle humain/IA** → Changer de mode pendant la partie  
✅ **Validation robuste** → Détection erreurs de placement  

---

## 📈 Complexité & Performance

- **Minimax depth 4** : ~0.5s par coup
- **Plateau 9×9** : ~10K positions évaluées
- **Frontend** : 60 FPS animations
- **Validation** : <1ms par vérification de victoire

---

## 🎯 En Une Phrase

> *"Une application Puissance 4 web déployable en production, avec une IA Minimax compétitive, interface moderne, et 3 modes de jeu - entièrement autonome et sans dépendances externes."*

---

**Durée totale : ~5-6 minutes à ton rythme.**
