# 🤖 Système ML - Import, Entraînement et Prédiction

## 📋 Vue d'ensemble

Le système ML permet de :
1. **Importer des parties** au format TXT (colonnes jouées)
2. **Entraîner des modèles** à partir de la base de données
3. **Prédire** le gagnant et le nombre de coups

## 🎯 Format des parties TXT

### Structure
```
4534562718
```

- **Colonnes 1-9** (numérotation de 1 à 9)
- **Ordre chronologique** des coups
- **Rouge commence toujours** (index 0, 2, 4...)
- **Jaune joue après** (index 1, 3, 5...)

### Exemples

**Partie courte (Rouge gagne fast)**
```
444
```
- Coup 1 (Rouge): Colonne 4
- Coup 2 (Jaune): Colonne 4
- Coup 3 (Rouge): Colonne 4
→ Rouge aligne 3 pions (mais besoin de 4 pour gagner)

**Partie classique**
```
45345623456789
```
- 14 coups alterné Rouge/Jaune
- Progressif, construit une stratégie

## 🖥️ Utilisation - Interface Web

### 1. Importer une Partie

```
📊 ML Training & Import
  ├─ Importer Partie TXT (ex: 4534562)
  │  └─ [Champ texte] → [📥 Importer Partie]
```

**Étapes:**
1. Cliquez sur "📊 ML Training & Import" (développer le panneau)
2. Entrez les colonnes: `4534562`
3. Cliquez `📥 Importer Partie`
4. ✅ La partie est sauvegardée en BDD

**Exemple d'erreur:**
```
❌ ERREUR: Colonne invalide: 10
   (colonnes doivent être 1-9)

❌ ERREUR: Colonne 5 pleine au coup 8
   (colonne remplie, pion ne peut pas descendre)
```

### 2. Entraîner le Modèle ML

```
  ├─ [🤖 Entraîner Modèle ML]
```

**Étapes:**
1. Assurez d'avoir au moins **5 parties importées**
2. Cliquez `🤖 Entraîner Modèle ML`
3. Attendre ~5-10 secondes (selon le nombre de parties)
4. ✅ Modèles sauvegardés:
   - `model_winner.joblib` → Classifie le gagnant
   - `model_moves.joblib` → Estime les coups

**Résultat attendu:**
```
✅ Modèle entraîné!
📊 Parties traitées: 50
🎯 Précision (gagnant): 87.4%
📈 R² score (coups): 0.92
```

### 3. Prédire avec le Modèle

```
  ├─ [🔮 Prédire avec ML]
```

**Étapes:**
1. Disposez des pions sur le plateau (mode éditeur 🎨)
2. Cliquez sur "🔮 Prédire avec ML"
3. Attendez l'analyse (~1 seconde)
4. Résultat complet s'affiche:
   - Gagnant probable
   - Coups estimés
   - Probabilités par joueur

**Exemple de résultat:**
```
🔮 Prédiction ML:
🏆 Joueur 2 (Jaune 🟡)
⏱️ ~12 coups
📊 Probabilités:
  🔴 Rouge gagne: 23.4%
  🟡 Jaune gagne: 71.2%
  🤝 Égalité: 5.4%
💪 Confiance: 71.2%
```

## 🔧 API REST

### Endpoint 1: Import de Partie

```http
POST /api/import_game
Content-Type: application/json

{
  "moves": "4534562"
}
```

**Réponse succès:**
```json
{
  "success": true,
  "game_id": 42,
  "moves_count": 7,
  "message": "Partie importée avec 7 coups"
}
```

**Réponse erreur:**
```json
{
  "error": "Colonne 5 pleine au coup 8"
}
```

### Endpoint 2: Entraîner le Modèle

```http
POST /api/train_model_from_db
Content-Type: application/json
```

**Réponse:**
```json
{
  "success": true,
  "games_processed": 50,
  "model_winner_accuracy": 0.874,
  "model_moves_r2": 0.92,
  "message": "Modèles entraînés et sauvegardés"
}
```

### Endpoint 3: Prédiction ML

```http
POST /api/predict_ml
Content-Type: application/json

{
  "grid": [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 2, 1, 2, 1, 0, 0, 0, 0]
  ]
}
```

**Réponse:**
```json
{
  "success": true,
  "winner": "Joueur 1 (Rouge 🔴)",
  "moves_to_win": 8,
  "prediction": "Joueur 1 (Rouge 🔴) devrait gagner en ~8 coups",
  "confidence": 0.712,
  "probabilities": {
    "red_wins": 0.712,
    "yellow_wins": 0.234,
    "draw": 0.054
  }
}
```

## 📊 Entraînement ML - Détails Techniques

### Features (Entrées du modèle)

| Feature | Description | Exemple |
|---------|-------------|---------|
| `p1_count` | Nombre de pions Rouge | 12 |
| `p2_count` | Nombre de pions Jaune | 11 |
| `score` | Évaluation Minimax du plateau | 450 |
| `move_count` | Nombre total de coups | 23 |

### Modèles Utilisés

**1. RandomForestClassifier** (Gagnant)
- Entrée: Features (4 dimensions)
- Sortie: [0=Red, 1=Yellow, 2=Draw]
- Métriques: Accuracy, Precision, Recall

**2. RandomForestRegressor** (Coups)
- Entrée: Features (4 dimensions)
- Sortie: Coups estimés (0-60)
- Métriques: MAE, R², MSE

### Données d'Entraînement Sources

| Source | Nombre | Format |
|--------|--------|--------|
| BDD Parties Web | Variable | Colonnes (base 1) |
| Import TXT | Variable | Colonnes (base 1) |
| Parties IA | Optionnel | Colonnes (base 1) |

## 🔄 Workflow Complet

### Étape 1: Préparer les Données

```bash
# Option A: Générer des parties automatiquement
python3 generate_test_games.py 50
# → Génère et importe 50 parties aléatoires

# Option B: Importer manuellement
# Via l'UI: Importer Partie TXT (4534562, etc.)
```

### Étape 2: Entraîner

```bash
# Via l'UI: Clic sur "🤖 Entraîner Modèle ML"
# Attend: 5-30 secondes selon nombre de parties
# Résultat: model_winner.joblib + model_moves.joblib
```

### Étape 3: Prédire

```bash
# Via l'UI: Éditeur 🎨 → Disposer pions → "🔮 Prédire avec ML"
# Résultat: Gagnant + Coups + Probabilités
```

## 📝 Cas d'Usage

### Cas 1: Tester une Position Personnalisée

1. Cliquez sur 🎨 Éditeur
2. Placez des pions (Red/Yellow)
3. Validez (différence pions ≤ 1)
4. "Jouer depuis l'éditeur"
5. Cliquez "🔮 Prédire avec ML"
6. → Résultat instantané

### Cas 2: Analyser un Dataset Historique

1. Convertissez vos parties (ex: PGN) → Format TXT
2. Pour chaque partie: Importez via l'UI
3. Une fois suffisamment de parties (10+): Entraînez
4. Prédisez sur nouvelles positions

### Cas 3: Améliorer les Modèles

1. Récoltez plus de parties (50+)
2. Ré-entraînez pour meilleure précision
3. Comparez: Accélération? Meilleure confiance?
4. Déployer en production

## 🚨 Limitations & Futur

### Limitations Actuelles
- ❌ Modèle n'apprend qu'avec coups simples
- ❌ Pas de stratégies avancées (blocages multiples)
- ❌ Plateaux 9×9 seulement

### Améliorations Futures
- ✅ Ajouter features: "Alignements proches", "Blocages critiques"
- ✅ Utiliser Deep Learning (CNN) sur plateau entier
- ✅ Support plateaux variables (6×7, 8×8, etc.)
- ✅ Feedback utilisateur pour réentrainement

## 🐛 Troubleshooting

### Erreur: "Modèles non entraînés"
```
Cause: Fichiers model_*.joblib manquants
Solution: Cliquez "🤖 Entraîner Modèle ML"
```

### Erreur: "Insuffisant de parties"
```
Cause: < 10 parties en BDD
Solution: Importez plus de parties TXT
          Ou: python3 generate_test_games.py 50
```

### Erreur: "Colonne invalide"
```
Cause: Chiffre > 9 ou < 1
Solution: Format: barres 1-9 uniquement
          ✅ "45345" (5 colonnes)
          ❌ "4534510" (10 invalide)
```

## 📚 Ressources

- [Source Code API](app.py#L1097)
- [Frontend JS](templates/index.html)
- [Générateur Test](generate_test_games.py)
- [Database Schema](app.py#L557)

---

**Dernière mise à jour:** 15 avril 2026  
**Statut:** ✅ Production Ready
