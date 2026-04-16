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
    
    # 2️⃣ Récupérer TOUTES les parties COMPLÈTES (TERMINEE)
    print("\n2️⃣ Extraction des parties...")
    try:
        # On prend les games TERMINEES (il y a 20472 games!)
        cursor.execute("""
            SELECT coups FROM games 
            WHERE statut = 'TERMINEE' AND coups IS NOT NULL
        """)
        coups_list = [row[0] for row in cursor.fetchall()]
        print(f"✅ {len(coups_list)} parties TERMINEES chargées")
        
    except Exception as e:
        print(f"❌ Erreur extraction: {e}")
        return False
    
    # 3️⃣ Feature engineering + détection du gagnant
    print("\n3️⃣ Feature engineering + détection gagnant...")
    
    def check_winner(board):
        """Détecte le gagnant sur le plateau 8x9"""
        # Horizontal
        for row in range(8):
            for col in range(6):
                if board[row][col] != 0:
                    if board[row][col] == board[row][col+1] == board[row][col+2] == board[row][col+3]:
                        return board[row][col]
        # Vertical
        for col in range(9):
            for row in range(5):
                if board[row][col] != 0:
                    if board[row][col] == board[row+1][col] == board[row+2][col] == board[row+3][col]:
                        return board[row][col]
        # Diagonal /
        for row in range(5, 8):
            for col in range(6):
                if board[row][col] != 0:
                    if board[row][col] == board[row-1][col+1] == board[row-2][col+2] == board[row-3][col+3]:
                        return board[row][col]
        # Diagonal \
        for row in range(5):
            for col in range(6):
                if board[row][col] != 0:
                    if board[row][col] == board[row+1][col+1] == board[row+2][col+2] == board[row+3][col+3]:
                        return board[row][col]
        return 0  # Draw
    
    X = []
    y_winner = []
    y_moves = []
    
    for coups in coups_list:
        try:
            # Parse coups
            moves = [int(c) for c in coups]
            
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
            
            # Détecter gagnant
            winner = check_winner(board)
            
            # Features
            features = [
                p1_count,
                p2_count,
                len(moves),
                p1_count - p2_count
            ]
            
            X.append(features)
            y_winner.append(winner)  # 0=draw, 1=red, 2=yellow
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
    
    cursor.close()
    conn.close()
    
    return True

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    
    if success:
        print("✅ Les modèles sont prêts à prédire!")
    else:
        print("⚠️ Erreur lors de l'entraînement.")
    
    print("=" * 60 + "\n")
