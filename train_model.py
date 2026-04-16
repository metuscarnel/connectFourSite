#!/usr/bin/env python3
"""
Script pour entraîner le modèle ML avec TOUTES les données en BDD AlwaysData.
Se connecte DIRECTEMENT à AlwaysData (pas par API Flask).
"""

import mysql.connector
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
import joblib
import os

# 🔧 Configuration AlwaysData
DB_HOST = 'mysql-metuscarnel.alwaysdata.net'
DB_USER = 'metuscarnel'
DB_PASS = '$Maestro137#'
DB_NAME = 'metuscarnel_connect4'
DB_PORT = 3306

def main():
    print("=" * 60)
    print("🤖 Entraînement du Modèle ML - Données AlwaysData")
    print("=" * 60)
    
    # 1️⃣ Tester connexion BDD
    print("\n1️⃣ Connexion à AlwaysData...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM games;")
        game_count = cursor.fetchone()[0]
        print(f"✅ Connexion réussie!")
        print(f"   Hôte: {DB_HOST}")
        print(f"   Base: {DB_NAME}")
        print(f"   Parties en BDD: {game_count}")
        
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False
    
    # 2️⃣ Récupérer toutes les parties
    print("\n2️⃣ Extraction des parties...")
    try:
        cursor.execute("""
            SELECT game_state, winner FROM games 
            WHERE game_state IS NOT NULL AND winner IS NOT NULL
            LIMIT 1000
        """)
        games = cursor.fetchall()
        print(f"✅ {len(games)} parties chargées")
        
    except Exception as e:
        print(f"❌ Erreur extraction: {e}")
        return False
    
    # 3️⃣ Feature engineering
    print("\n3️⃣ Feature engineering...")
    X = []
    y_winner = []
    y_moves = []
    
    for game_state, winner in games:
        try:
            # Parse la séquence de coups
            moves = [int(c) for c in game_state]
            
            # Simuler le plateau
            board = [[0]*9 for _ in range(8)]
            p1_count = 0
            p2_count = 0
            
            for i, col in enumerate(moves):
                player = 1 if i % 2 == 0 else 2
                for row in range(7, -1, -1):
                    if board[row][col] == 0:
                        board[row][col] = player
                        if player == 1:
                            p1_count += 1
                        else:
                            p2_count += 1
                        break
            
            # Features
            features = [
                p1_count,
                p2_count,
                len(moves),  # move_count
                p1_count - p2_count  # piece_diff
            ]
            
            X.append(features)
            y_winner.append(int(winner))
            y_moves.append(len(moves))
            
        except:
            continue
    
    print(f"✅ {len(X)} parties traitées")
    
    if len(X) < 10:
        print("❌ Pas assez de données pour l'entraînement!")
        return False
    
    # 4️⃣ Split train/test
    print("\n4️⃣ Séparation train/test...")
    X_train, X_test, y_w_train, y_w_test, y_m_train, y_m_test = train_test_split(
        X, y_winner, y_moves, test_size=0.2, random_state=42
    )
    print(f"   Train: {len(X_train)}, Test: {len(X_test)}")
    
    # 5️⃣ Entraînement
    print("\n5️⃣ Entraînement RandomForest...")
    
    # Modèle gagnant
    model_winner = RandomForestClassifier(n_estimators=100, random_state=42)
    model_winner.fit(X_train, y_w_train)
    acc_winner = accuracy_score(y_w_test, model_winner.predict(X_test))
    
    # Modèle coups
    model_moves = RandomForestRegressor(n_estimators=100, random_state=42)
    model_moves.fit(X_train, y_m_train)
    r2_moves = r2_score(y_m_test, model_moves.predict(X_test))
    
    print(f"✅ Entraînement RÉUSSI!")
    
    # 6️⃣ Sauvegarder
    print("\n6️⃣ Sauvegarde des modèles...")
    joblib.dump(model_winner, 'model_winner.joblib')
    joblib.dump(model_moves, 'model_moves.joblib')
    
    print(f"\n✅ Modèles sauvegardés!")
    print(f"\n📊 Résultats:")
    print(f"   Parties traitées: {len(X)}")
    print(f"   🎯 Précision (gagnant): {acc_winner*100:.1f}%")
    print(f"   📈 R² Score (coups): {r2_moves:.3f}")
    print(f"\n✓ Fichiers générés:")
    print(f"   • model_winner.joblib")
            print(f"   • model_moves.joblib")
            
            return True
        else:
            print(f"\n❌ Erreur entraînement: {result.get('error', 'Inconnue')}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Timeout! L'entraînement a pris trop longtemps.")
        print("   (Mais le serveur continue probablement...)")
        return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    
    if success:
        print("✅ Le modèle est prêt à prédire!")
        print("   Teste avec: python3 test_predictions.py")
    else:
        print("⚠️ Erreur lors de l'entraînement.")
    
    print("=" * 60 + "\n")
