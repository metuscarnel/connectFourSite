#!/usr/bin/env python3
"""
Script pour générer et importer des parties de test au format TXT.
Usage:
    python3 generate_test_games.py  # Génère 10 parties de test
"""

import requests
import random

API_URL = "http://localhost:5001"  # À adapter selon votre déploiement

def generate_random_game():
    """Génère une partie aléatoire valide."""
    moves = []
    board = [[0] * 9 for _ in range(8)]
    
    for i in range(random.randint(7, 50)):  # Entre 7 et 50 coups
        col = random.randint(0, 8)
        
        # Trouver la première ligne vide
        row = None
        for r in range(7, -1, -1):
            if board[r][col] == 0:
                row = r
                break
        
        if row is None:
            # Colonne pleine
            continue
        
        # Placer le pion
        player = 1 if i % 2 == 0 else 2
        board[row][col] = player
        moves.append(str(col + 1))  # Convertir en base 1
    
    return ''.join(moves)

def import_games(count=10):
    """Importe plusieurs parties de test."""
    print(f"📥 Génération et import de {count} parties...")
    
    success = 0
    for i in range(1, count + 1):
        moves = generate_random_game()
        
        try:
            response = requests.post(
                f"{API_URL}/api/import_game",
                json={"moves": moves},
                timeout=5
            )
            result = response.json()
            
            if result.get("success"):
                print(f"✅ Partie {i}: {result['moves_count']} coups importés (ID: {result['game_id']})")
                success += 1
            else:
                print(f"❌ Partie {i}: {result.get('error', 'Erreur inconnue')}")
        
        except Exception as e:
            print(f"❌ Partie {i}: {e}")
    
    print(f"\n📊 Résultat: {success}/{count} parties importées")
    
    return success >= 5  # Au moins 5 parties pour entrainer

def train_model():
    """Entraîne le modèle ML."""
    print("\n🤖 Entraînement du modèle...")
    
    try:
        response = requests.post(
            f"{API_URL}/api/train_model_from_db",
            timeout=30
        )
        result = response.json()
        
        if result.get("success"):
            print(f"✅ Modèle entraîné!")
            print(f"   📊 Parties: {result['games_processed']}")
            print(f"   🎯 Précision: {result['model_winner_accuracy']*100:.1f}%")
            print(f"   📈 R² Score: {result['model_moves_r2']*100:.1f}%")
        else:
            print(f"❌ Erreur: {result.get('error', 'Inconnue')}")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    import sys
    
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    print("=" * 50)
    print("🎮 Générateur de parties Connect4")
    print("=" * 50)
    
    if import_games(count):
        train_model()
    else:
        print("\n⚠️ Pas assez de parties importées pour entraîner le modèle.")
        print("   Besoin d'au moins 5 parties valides.")
    
    print("\n" + "=" * 50)
