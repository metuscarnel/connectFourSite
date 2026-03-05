# 🎮 GUIDE RAPIDE - Puissance 4 Web

## 🚀 Lancement Rapide

```bash
# 1. Aller dans le dossier deployFour
cd "/Users/metusgbogbohoundada/Documents/CILS 2025/SEMESTRE 06/ConnectFour/deployFour"

# 2. Lancer le serveur
python app.py

# 3. Ouvrir le navigateur
# http://localhost:5001
```

## 🎯 Modes Disponibles

| Mode | Description |
|------|-------------|
| **Joueur vs Joueur** | 2 joueurs humains |
| **Joueur vs IA** | Humain (Rouge) vs IA (Jaune) |
| **IA vs IA** | Mode spectateur automatique |

## 🤖 Difficulté IA

- **Facile** : Aléatoire
- **Difficile** : Minimax (profondeur 4)

## ✅ Fichiers Créés/Modifiés

```
deployFour/
├── app.py ✅                 # Backend Flask avec API REST complète
├── templates/
│   └── index.html ✅         # Frontend avec 3 modes de jeu
├── requirements.txt ✅       # Dépendances (Flask, numpy, etc.)
└── README.md ✅              # Documentation complète
```

## 🔧 Commandes Utiles

```bash
# Vérifier que le serveur tourne
curl http://localhost:5001/health

# Arrêter le serveur
# CTRL+C dans le terminal

# Redémarrer
python app.py
```

## 📊 Statut

✅ Backend Flask opérationnel  
✅ Frontend moderne et réactif  
✅ 3 modes de jeu fonctionnels  
✅ IA Minimax et Random intégrées  
✅ Animations et effets visuels  
✅ Détection de victoire automatique  
✅ Documentation complète  

**🎮 Application prête à l'emploi !**
