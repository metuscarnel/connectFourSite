# 📚 Exemple Complet - ML Training & Prédiction

## 🎯 Scénario: Importer 10 Parties & Prédire

### **Étape 1: Préparer les Données (Format TXT)**

Voici **10 parties au format TXT** prêtes à importer:

```
Partie 1: 4534562      (7 coups)
Partie 2: 45345678     (8 coups)
Partie 3: 4567854      (7 coups)
Partie 4: 3456247      (7 coups)
Partie 5: 4444         (4 coups - Rouge gagne!)
Partie 6: 5555         (4 coups - Jaune gagne!)
Partie 7: 123456789    (9 coups)
Partie 8: 987654321    (9 coups)
Partie 9: 454545       (6 coups)
Partie 10: 565656      (6 coups)
```

---

## 🖥️ Exemple Manuel - Interface Web

### **Étape 1: Importer chaque partie**

**Formule à suivre:**
```
Cliquez: 📊 ML Training & Import
         ↓
Entrez: 4534562
         ↓
Cliquez: 📥 Importer Partie
         ↓
Résultat: ✅ Partie importée! ID: 1 - 7 coups
```

**Résultat complet après 10 imports:**

```
✅ Partie 1 importée! ID: 1 - 7 coups
✅ Partie 2 importée! ID: 2 - 8 coups
✅ Partie 3 importée! ID: 3 - 7 coups
✅ Partie 4 importée! ID: 4 - 7 coups
✅ Partie 5 importée! ID: 5 - 4 coups
✅ Partie 6 importée! ID: 6 - 4 coups
✅ Partie 7 importée! ID: 7 - 9 coups
✅ Partie 8 importée! ID: 8 - 9 coups
✅ Partie 9 importée! ID: 9 - 6 coups
✅ Partie 10 importée! ID: 10 - 6 coups

📊 Total: 10 parties en BDD
```

---

### **Étape 2: Entraîner le Modèle**

```
Cliquez: 🤖 Entraîner Modèle ML
Attendre: ⏳ 5-10 secondes...

Résultat:
┌────────────────────────────────────┐
│ ✅ Entraînement réussi!             │
│                                    │
│ 📊 Parties traitées: 10            │
│ 🎯 Précision (gagnant): 78.5%      │
│ 📈 R² Score (coups): 0.87          │
│                                    │
│ ✓ model_winner.joblib sauvegardé   │
│ ✓ model_moves.joblib sauvegardé    │
└────────────────────────────────────┘
```

---

### **Étape 3: Prédire une Position**

**Scénario:** Tu as créé une position artistique au plateau:

```
🎨 Éditeur (Position personnalisée)
├─ Ligne 7 (bas): [🔴 🔴 🔴 🟡 🟡 🟡 ⚪ ⚪ ⚪]
├─ Ligne 6:       [⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪]
├─ Ligne 5:       [⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪]
└─ Autres:        [⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪]

Feature d'entrée:
p1_count = 3 (3 pions Rouges)
p2_count = 3 (3 pions Jaunes)
minimax_score = 45
move_count = 6
```

**Action:** Cliquez `🔮 Prédire avec ML`

**Résultat:**

```
┌──────────────────────────────────────┐
│ 🔮 Prédiction ML:                    │
│                                      │
│ 🏆 Joueur 1 (Rouge 🔴)              │
│ ⏱️ ~8 coups                          │
│                                      │
│ 📊 Probabilités:                     │
│   🔴 Rouge gagne: 62.3%              │
│   🟡 Jaune gagne: 31.5%              │
│   🤝 Égalité: 6.2%                   │
│                                      │
│ 💪 Confiance: 62.3%                  │
└──────────────────────────────────────┘
```

---

## 🚀 Exemple en Ligne de Commande

### **Option: Script Python Automatique**

```bash
cd deployFour
python3 generate_test_games.py 10
```

**Sortie console:**

```
==================================================
🎮 Générateur de parties Connect4
==================================================
📥 Génération et import de 10 parties...
✅ Partie 1: 7 coups importés (ID: 1)
✅ Partie 2: 8 coups importés (ID: 2)
✅ Partie 3: 5 coups importés (ID: 3)
✅ Partie 4: 9 coups importés (ID: 4)
✅ Partie 5: 6 coups importés (ID: 5)
✅ Partie 6: 4 coups importés (ID: 6)
✅ Partie 7: 11 coups importés (ID: 7)
✅ Partie 8: 7 coups importés (ID: 8)
✅ Partie 9: 8 coups importés (ID: 9)
✅ Partie 10: 6 coups importés (ID: 10)

📊 Résultat: 10/10 parties importées

🤖 Entraînement du modèle...
✅ Modèle entraîné!
   📊 Parties: 10
   🎯 Précision: 75.3%
   📈 R² Score: 0.84

==================================================
```

---

## 📊 Détails Techniques - Exemple Réel

### **Données d'Entraînement (Matrice X & y)**

Après import et traitement des 10 parties:

```python
# Partie 1: "4534562" (7 coups, Égalité)
X[0] = [3, 4, 52, 7]    →  y_winner[0] = 2   y_moves[0] = 7

# Partie 2: "45345678" (8 coups, Yellow wins)
X[1] = [4, 4, 38, 8]    →  y_winner[1] = 1   y_moves[1] = 8

# Partie 3: "4567854" (7 coups, Red wins)
X[2] = [4, 3, 71, 7]    →  y_winner[2] = 0   y_moves[2] = 7

# Partie 4: "3456247" (7 coups, Égalité)
X[3] = [3, 4, 45, 7]    →  y_winner[3] = 2   y_moves[3] = 7

# Partie 5: "4444" (4 coups, Red wins fast!)
X[4] = [2, 1, 150, 4]   →  y_winner[4] = 0   y_moves[4] = 4

# Partie 6: "5555" (4 coups, Yellow wins fast!)
X[5] = [1, 2, -180, 4]  →  y_winner[5] = 1   y_moves[5] = 4

# ... (4 autres)
```

---

## 🔍 Prédiction En Détail

### **Position Nouvelle:**

```
Plateau édité:
    Col: 1 2 3 4 5 6 7 8 9
Ligne 8:    ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪
Ligne 7:    ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪
Ligne 6:    ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪
Ligne 5:    ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪
Ligne 4:    ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪
Ligne 3:    ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪
Ligne 2:    ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪
Ligne 1:    🔴 🔴 🔴 🟡 🟡 🟡 ⚪ ⚪ ⚪
           (3R, 3Y)

Current Player: 🔴 (Rouge, c'est à son tour)
```

### **Calcul des Features**

```python
# Compter pions
p1_count = 3  # Rouges
p2_count = 3  # Jaunes

# Évaluation Minimax de la position
ai = MinimaxAI(depth=2)
score = ai.score_position(board, PLAYER1=Red)
      # Algorithme d'évaluation...
      → score = 62

# Coups joués jusqu'ici
move_count = p1_count + p2_count = 6

# Vecteur final
features = [3, 3, 62, 6]
```

### **Prédiction (Appel au Modèle)**

```python
model_winner = joblib.load('model_winner.joblib')
model_moves = joblib.load('model_moves.joblib')

# Prédiction du gagnant
prediction = model_winner.predict([[3, 3, 62, 6]])
             → [0]  (Classe 0 = Red wins)

# Probabilités
proba = model_winner.predict_proba([[3, 3, 62, 6]])
        → [[0.623, 0.315, 0.062]]
           (62.3% Red, 31.5% Yellow, 6.2% Draw)

# Prédiction des coups
moves_pred = model_moves.predict([[3, 3, 62, 6]])
             → [7.8]  (≈ 8 coups estimés)
```

### **Résultat Affiché**

```
🏆 Joueur 1 (Rouge 🔴) devrait gagner
⏱️ ~8 coups estimés
💪 Confiance: 62.3%

Répartition:
🔴 62.3% (Very Likely)
🟡 31.5% (Possible)
🤝 6.2% (Unlikely)
```

---

## 🎲 Scénario 2: Position Équilibrée

### **Position Différente:**

```
Plateau:
    1 2 3 4 5 6 7 8 9
    ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪
    ⚪ ⚪ ⚪ 🟡 ⚪ ⚪ ⚪ ⚪ ⚪
    ⚪ ⚪ 🔴 🟡 ⚪ ⚪ ⚪ ⚪ ⚪
    ⚪ 🔴 🟡 🔴 🟡 ⚪ ⚪ ⚪ ⚪
    🟡 🔴 🟡 🔴 🟡 ⚪ ⚪ ⚪ ⚪
    🔴 🔴 🟡 🔴 🟡 ⚪ ⚪ ⚪ ⚪
    🔴 🟡 🔴 🟡 🔴 ⚪ ⚪ ⚪ ⚪
           ↑
        Beaucoup de pions au centre!

p1_count = 7, p2_count = 6
```

### **Prédiction:**

```
features = [7, 6, 89, 13]

Résultat:
🏆 Indéterminé (partie équilibrée)
⏱️ ~11 coups

🔴 45.2% (Probable)
🟡 44.8% (Probable)
🤝 10.0% (Possible)

💪 Confiance: 45.2%
```

---

## ⚠️ Cas Limites

### **Partie 1: Victoire Rapide (4 coups)**

```
Série "4444":
Coup 1 (Red):   🔴 placé col 4
Coup 2 (Yellow): 🟡 placé col 4
Coup 3 (Red):   🔴 placé col 4
Coup 4 (Yellow): 🟡 placé col 4
Coup 5 rejected (colonne pleine)

Résultat: Partie terminée, 🟡 gagne!

Features: [2, 2, 200, 4]
Target: winner = 1 (Yellow), moves = 4
```

### **Prédiction d'une Position Similaire:**

```
Situation:
    🔴
    🟡
    🔴
    🟡
    (colonne presque pleine)

Résultat:
🟡 Jaune gagne très probablement
⏱️ ~1 coup
💪 Confiance: 98.5%
```

---

## 🔄 Import Depuis Fichier TXT (Avancé)

### **Créer un fichier `parties.txt`:**

```txt
4534562
45345678
4567854
3456247
4444
5555
123456789
987654321
454545
565656
```

### **Script Python Pour Import:**

```python
with open('parties.txt', 'r') as f:
    for i, line in enumerate(f):
        moves = line.strip()
        if not moves:
            continue
        
        # Import via API
        response = requests.post(
            'http://localhost:5001/api/import_game',
            json={'moves': moves}
        )
        
        if response.json().get('success'):
            print(f"✅ Partie {i+1} importée")
        else:
            print(f"❌ Erreur partie {i+1}: {response.json()['error']}")

# À la fin:
# python3 -m requests.post http://localhost:5001/api/train_model_from_db
```

---

## 📈 Résumé Graphique

```
┌──────────────────┐
│  10 Parties      │  Texte: 4534562, 4444, ...
│  (Format TXT)    │
└────────┬─────────┘
         │ IMPORT
         ▼
┌──────────────────┐
│  10 Parties      │  BDD: coups stored
│  (Base de        │
│   Données)       │
└────────┬─────────┘
         │ EXTRACT FEATURES
         ▼
┌──────────────────────┐
│  X = (10, 4)         │  [[3,4,52,7], ..., [1,2,-180,4]]
│  y_winner = (10,)    │  [2, 1, 0, 2, 0, 1, ...]
│  y_moves = (10,)     │  [7, 8, 7, 7, 4, 4, ...]
└────────┬─────────────┘
         │ TRAIN ML (2 models)
         ▼
┌──────────────────────────┐
│  RandomForestClassifier  │  winner.joblib
│  + RandomForestRegressor │  moves.joblib
│  (100 trees each)        │
└────────┬─────────────────┘
         │
    ┌────┴────┐
    │ PREDICT │
    └────┬────┘
         ▼
┌──────────────────────┐
│  New Position        │  + Proba (62%, 31%, 6%)
│  [3, 3, 62, 6]       │  + Moves (8)
│  → Red wins, ~8 coups│
└──────────────────────┘
```

---

## ✅ Checklist - Exemple Complet

- [ ] Générer 10 parties (`python3 generate_test_games.py 10`)
- [ ] Vérifier import en BDD
- [ ] Cliquer "🤖 Entraîner Modèle ML"
- [ ] Vérifier fichiers: `model_winner.joblib`, `model_moves.joblib`
- [ ] Créer position test avec 🎨 Éditeur
- [ ] Cliquer "🔮 Prédire avec ML"
- [ ] ✅ Vérifier résultat intelligible!

---

**Besoin d'un exemple encore plus spécifique?** Demande moi! 🚀
