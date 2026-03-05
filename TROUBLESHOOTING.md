# 🔧 Guide de Dépannage - Puissance 4 Web

## ❌ Problème : "Je n'arrive pas à jouer"

### ✅ Solutions Appliquées

1. **Initialisation automatique** : Le jeu démarre maintenant automatiquement au chargement de la page
2. **Feedback visuel amélioré** : Les cases vides s'illuminent au survol
3. **Logs de débogage** : Ouvre la console navigateur (F12) pour voir les clics détectés

### 🔍 Comment Vérifier

#### 1️⃣ Ouvre la console du navigateur
- **Chrome/Edge** : `F12` ou `Cmd+Option+I` (Mac)
- **Firefox** : `F12` ou `Cmd+Shift+K` (Mac)
- **Safari** : `Cmd+Option+C` (activer d'abord dans Préférences → Avancé)

#### 2️⃣ Rafraîchis la page
- Appuie sur `F5` ou `Cmd+R` (Mac)
- Tu devrais voir : "État du jeu: gameActive=true..."

#### 3️⃣ Clique sur une colonne
Dans la console, tu devrais voir :
```
🖱️ Clic détecté sur colonne 4
État du jeu: gameActive=true, isAIThinking=false, gameMode=pvp, currentPlayer=1
✅ Placement du jeton joueur 1 dans colonne 4
```

#### 4️⃣ Vérifie le statut
- En haut du plateau : "Tour du Joueur 1 (Rouge 🔴)"
- Le message change après chaque coup

### 🐛 Diagnostics Possibles

#### ❌ "Clic ignoré : jeu inactif"
**Cause** : `gameActive = false`  
**Solution** : Clique sur "🎲 Nouvelle Partie"

#### ❌ "Colonne pleine !"
**Cause** : La colonne a déjà 9 jetons  
**Solution** : Choisis une autre colonne

#### ❌ Rien ne se passe au clic
**Causes possibles** :
1. Le serveur Flask n'est pas lancé
2. Erreur JavaScript (vérifier console)
3. Navigateur en cache (rafraîchir avec `Cmd+Shift+R`)

**Solutions** :
```bash
# 1. Vérifier que le serveur tourne
curl http://localhost:5001/health

# 2. Si erreur, relancer le serveur
cd deployFour
python app.py

# 3. Vider le cache navigateur
# Chrome : Cmd+Shift+Delete → Cocher "Images et fichiers en cache"
```

#### ❌ Erreur "Failed to fetch" dans la console
**Cause** : Le serveur Flask est arrêté  
**Solution** :
```bash
cd "/Users/metusgbogbohoundada/Documents/CILS 2025/SEMESTRE 06/ConnectFour/deployFour"
"/Users/metusgbogbohoundada/Documents/CILS 2025/SEMESTRE 06/ConnectFour/.venv/bin/python" app.py
```

### ✅ Checklist de Vérification

- [ ] Le serveur Flask affiche "Running on http://127.0.0.1:5001"
- [ ] La page http://localhost:5001 s'ouvre sans erreur
- [ ] Le plateau de 9×9 cases est visible
- [ ] Le message affiche "Tour du Joueur 1 (Rouge 🔴)"
- [ ] Les cases vides s'illuminent au survol de la souris
- [ ] Un clic sur une case ajoute un jeton rouge
- [ ] Le message passe à "Tour du Joueur 2 (Jaune 🟡)"
- [ ] Un deuxième clic ajoute un jeton jaune

### 🎮 Test Rapide (Mode PvP)

1. Rafraîchis la page (`F5`)
2. Vérifie : "Tour du Joueur 1 (Rouge 🔴)"
3. Clique sur la **colonne du milieu (4)**
4. → Un jeton **rouge** tombe en bas
5. → Message : "Tour du Joueur 2 (Jaune 🟡)"
6. Clique sur la **même colonne**
7. → Un jeton **jaune** tombe au-dessus du rouge
8. Continue jusqu'à aligner 4 jetons
9. → Message : "🏆 Joueur X (Couleur) a gagné !"
10. → Les 4 jetons gagnants clignotent

### 🤖 Test Mode IA

1. Sélectionne "Joueur vs IA"
2. Choisis "Difficile (Minimax)"
3. Clique "🎲 Nouvelle Partie"
4. Clique sur une colonne → Jeton rouge tombe
5. Attends 1 seconde → L'IA joue (jeton jaune)
6. Continue à jouer

### 🔄 Test Mode IA vs IA

1. Sélectionne "IA vs IA"
2. Choisis "Difficile (Minimax)"
3. Clique "🎲 Nouvelle Partie"
4. → Les deux IA jouent toutes seules !
5. Regarde le match en spectateur

### 📞 Support

Si le problème persiste :

1. **Vérifie les logs du serveur Flask** dans le terminal
2. **Regarde la console navigateur** (F12) pour les erreurs JavaScript
3. **Teste l'API manuellement** :
   ```bash
   curl -X POST http://localhost:5001/api/check_win \
     -H "Content-Type: application/json" \
     -d '{"grid":[[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]}'
   ```

### 🎯 Résumé des Changements

| Avant | Après |
|-------|-------|
| Plateau vide non jouable | ✅ Jeu initialisé automatiquement |
| Message générique | ✅ "Cliquez sur une colonne..." |
| Pas de feedback visuel | ✅ Cases illuminées au survol |
| Pas de logs | ✅ Console avec détails des clics |

**🎮 Le jeu devrait maintenant être jouable immédiatement !**
