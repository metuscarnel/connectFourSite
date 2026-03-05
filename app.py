"""
Application Flask pour le jeu Puissance 4 Web.
Fournit une interface web et des APIs pour l'IA.
Version PRO avec : BDD, Pause, Profondeur configurable, Scores Minimax en direct.

IMPORTANT: Utilise le même système de sauvegarde que le jeu desktop (db_manager.py)
"""

import sys
import os
import random
import json
import numpy as np
from flask import Flask, render_template, request, jsonify

# Ajout du chemin parent pour importer les modules src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.board import Board
from src.ai.minimax_ai import MinimaxAI
from src.ai.random_ai import RandomAI
from src.utils.constants import EMPTY, PLAYER1, PLAYER2, WIN_LENGTH, ROWS, COLS
from src.utils.db_manager import DatabaseManager

app = Flask(__name__)

# ============================================================
# CONFIGURATION BASE DE DONNÉES (via DatabaseManager local)
# On configure les variables d'environnement pour db_manager
# ============================================================
os.environ['DB_HOST'] = "mysql-metuscarnel.alwaysdata.net"
os.environ['DB_USER'] = "metuscarnel"
os.environ['DB_PASSWORD'] = "$Maestro137#"
os.environ['DB_NAME'] = "metuscarnel_connect4"
os.environ['DB_PORT'] = "3306"

# Instance globale du DatabaseManager (même que le jeu desktop)
db_manager = DatabaseManager()


# ============================================================
# INSTANCIATION DES IA
# ============================================================
minimax_ai = MinimaxAI(depth=4, name="Minimax Web")
random_ai = RandomAI(name="Random Web")


@app.route('/')
def index():
    """Page d'accueil avec le jeu."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Endpoint de santé pour vérifier que le serveur fonctionne."""
    return jsonify({"status": "ok", "message": "Puissance 4 Web est opérationnel!"})


@app.route('/api/get_ai_move', methods=['POST'])
def get_ai_move():
    """
    API pour obtenir le coup de l'IA avec scores Minimax.
    
    Attend:
        - grid: Grille 2D représentant le plateau (liste de listes)
        - ai_type: "minimax" ou "random"
        - player: 1 ou 2 (le joueur que l'IA contrôle)
        - depth: Profondeur de recherche Minimax (1-6)
    
    Retourne:
        - success: True/False
        - column: Colonne choisie par l'IA (0-indexed)
        - column_scores: Dictionnaire des scores par colonne (Minimax uniquement)
        - error: Message d'erreur si échec
    """
    try:
        data = request.get_json()
        grid_data = data.get('grid')
        ai_type = data.get('ai_type', 'minimax')
        player = data.get('player', PLAYER2)
        depth = data.get('depth', 4)
        
        if grid_data is None:
            return jsonify({"success": False, "error": "Grille manquante"}), 400
        
        # Reconstruction du Board à partir de la grille reçue
        rows = len(grid_data)
        cols = len(grid_data[0]) if rows > 0 else 0
        
        board = Board(rows=rows, cols=cols)
        
        # IMPORTANT: La grille frontend est inversée (row 0 = haut visuel)
        # On doit convertir pour notre convention (row 0 = bas physique)
        for r in range(rows):
            for c in range(cols):
                # Inversion : front[r] -> back[rows-1-r]
                board.grid[rows - 1 - r][c] = grid_data[r][c]
        
        column_scores = {}
        
        # Sélection de l'IA
        if ai_type == 'minimax':
            # Mise à jour de la profondeur dynamique
            minimax_ai.depth = int(depth)
            minimax_ai.set_player(player)
            
            # Calcul des scores Minimax pour chaque colonne valide
            valid_locations = board.get_valid_locations()
            best_score = float('-inf')
            best_column = valid_locations[0] if valid_locations else None
            
            for col in valid_locations:
                row = board.get_next_open_row(col)
                if row is not None:
                    temp_board = board.copy()
                    temp_board.drop_piece(row, col, player)
                    
                    # Évaluer avec Minimax (adversaire joue après)
                    _, score = minimax_ai.minimax(
                        temp_board,
                        minimax_ai.depth - 1,
                        float('-inf'),
                        float('inf'),
                        False  # Adversaire joue après notre coup
                    )
                    column_scores[col] = int(score)
                    
                    if score > best_score:
                        best_score = score
                        best_column = col
            
            column = best_column
        else:  # random
            column = random_ai.get_move(board)
        
        if column is None:
            return jsonify({"success": False, "error": "Aucun coup possible"}), 200
        
        return jsonify({
            "success": True,
            "column": column,
            "column_scores": column_scores
        })
    
    except Exception as e:
        print(f"[API ERROR] get_ai_move: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/check_win', methods=['POST'])
def check_win():
    """
    API pour vérifier la victoire ou l'égalité.
    
    Attend:
        - grid: Grille 2D représentant le plateau
    
    Retourne:
        - game_over: True si la partie est terminée
        - winner: 1 ou 2 (ou None si égalité/en cours)
        - winning_line: Liste des positions gagnantes [{row, col}, ...]
        - is_draw: True si égalité
    """
    try:
        data = request.get_json()
        grid_data = data.get('grid')
        
        if grid_data is None:
            return jsonify({"game_over": False, "error": "Grille manquante"}), 400
        
        rows = len(grid_data)
        cols = len(grid_data[0]) if rows > 0 else 0
        
        board = Board(rows=rows, cols=cols)
        
        # Conversion de la grille frontend -> backend
        for r in range(rows):
            for c in range(cols):
                board.grid[rows - 1 - r][c] = grid_data[r][c]
        
        # Vérification victoire joueur 1
        if board.check_win(PLAYER1):
            positions = board.get_winning_positions(PLAYER1)
            # Reconversion des positions backend -> frontend
            winning_line = [{"row": rows - 1 - r, "col": c} for r, c in positions]
            return jsonify({
                "game_over": True,
                "winner": PLAYER1,
                "winning_line": winning_line,
                "is_draw": False
            })
        
        # Vérification victoire joueur 2
        if board.check_win(PLAYER2):
            positions = board.get_winning_positions(PLAYER2)
            winning_line = [{"row": rows - 1 - r, "col": c} for r, c in positions]
            return jsonify({
                "game_over": True,
                "winner": PLAYER2,
                "winning_line": winning_line,
                "is_draw": False
            })
        
        # Vérification égalité (plateau plein)
        if board.is_full():
            return jsonify({
                "game_over": True,
                "winner": None,
                "winning_line": [],
                "is_draw": True
            })
        
        # Partie en cours
        return jsonify({
            "game_over": False,
            "winner": None,
            "winning_line": [],
            "is_draw": False
        })
    
    except Exception as e:
        print(f"[API ERROR] check_win: {e}")
        return jsonify({"game_over": False, "error": str(e)}), 500


# ============================================================
# ROUTES BASE DE DONNÉES (utilise DatabaseManager du jeu local)
# ============================================================

@app.route('/api/save', methods=['POST'])
def save_game():
    """
    Sauvegarde une partie terminée en utilisant le même système que le jeu desktop.
    
    Utilise DatabaseManager.insert_game() avec le format exact du jeu local :
    - coups : séquence de colonnes en Base 1 (ex: "5456734")
    - mode_jeu : "PvP", "PvAI", "AIvsAI" 
    - statut : "TERMINEE"
    - ligne_gagnante : JSON des positions gagnantes
    
    Attend:
        - historique_coups: String des colonnes jouées en Base 0 (ex: "4345623")
        - mode_jeu: Mode de jeu (optionnel, défaut: "Web")
        - ligne_gagnante: Liste des positions gagnantes (optionnel)
    
    Retourne:
        - success: True/False
        - message: Message de confirmation ou d'erreur
        - id: ID de la partie sauvegardée
    """
    try:
        data = request.get_json()
        historique_coups_base0 = data.get('historique_coups', '')
        mode_jeu = data.get('mode_jeu', 'Web')
        ligne_gagnante_raw = data.get('ligne_gagnante')  # Peut être un string JSON ou None
        
        # DEBUG: Afficher ce qui arrive du navigateur
        print(f"DEBUG SAVE - Ligne reçue: {ligne_gagnante_raw}")
        print(f"DEBUG SAVE - Type: {type(ligne_gagnante_raw)}")
        
        # CONVERSION CRITIQUE : Frontend Base 0 -> Backend Base 1
        # Le jeu desktop utilise des colonnes 1-9, le web utilise 0-8
        coups_base1 = ''.join(str(int(c) + 1) for c in historique_coups_base0)
        
        # Préparation de la ligne gagnante en JSON (si fournie)
        ligne_gagnante_json = None
        if ligne_gagnante_raw:
            # Le frontend envoie un string JSON, on le parse d'abord
            if isinstance(ligne_gagnante_raw, str):
                ligne_gagnante = json.loads(ligne_gagnante_raw)
            else:
                ligne_gagnante = ligne_gagnante_raw
            
            # Convertir les positions en Base 1 pour cohérence avec le desktop
            ligne_gagnante_base1 = [(pos['row'] + 1, pos['col'] + 1) for pos in ligne_gagnante]
            ligne_gagnante_json = json.dumps(ligne_gagnante_base1)
            print(f"DEBUG SAVE - Ligne convertie Base1: {ligne_gagnante_json}")
        
        # Connexion via DatabaseManager (même que le jeu desktop)
        if not db_manager.connect():
            return jsonify({
                "success": False,
                "error": "Connexion BDD échouée"
            }), 500
        
        try:
            # Création de la table si nécessaire
            db_manager.create_tables()
            
            # Insertion via la méthode du jeu desktop
            game_id = db_manager.insert_game(
                coups=coups_base1,
                mode_jeu=mode_jeu,
                statut="TERMINEE",
                ligne_gagnante=ligne_gagnante_json
            )
            
            if game_id is None:
                # Doublon détecté : mettre à jour ligne_gagnante si elle était NULL
                coups_symetrique = ''.join(str(10 - int(c)) for c in coups_base1)
                cursor = db_manager.connection.cursor(dictionary=True)
                
                # Récupérer l'ID du doublon
                cursor.execute(
                    "SELECT id, ligne_gagnante FROM games WHERE coups = %s OR coups = %s LIMIT 1",
                    (coups_base1, coups_symetrique)
                )
                existing = cursor.fetchone()
                
                if existing and ligne_gagnante_json:
                    # UPDATE ligne_gagnante si elle était vide
                    cursor.execute(
                        "UPDATE games SET ligne_gagnante = %s WHERE id = %s",
                        (ligne_gagnante_json, existing['id'])
                    )
                    db_manager.connection.commit()
                    print(f"DEBUG SAVE - Ligne mise à jour pour ID {existing['id']}")
                    cursor.close()
                    
                    return jsonify({
                        "success": True,
                        "message": f"Ligne gagnante mise à jour !",
                        "id": existing['id'],
                        "updated": True
                    })
                
                cursor.close()
                return jsonify({
                    "success": True,
                    "message": "Partie déjà existante",
                    "id": existing['id'] if existing else None,
                    "duplicate": True
                })
            
            return jsonify({
                "success": True,
                "message": f"Partie sauvegardée (format desktop) !",
                "id": game_id,
                "coups_base1": coups_base1
            })
            
        finally:
            db_manager.disconnect()
        
    except Exception as e:
        print(f"[API ERROR] save_game: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/historique')
def historique():
    """
    Affiche l'historique des parties en utilisant DatabaseManager.get_all_games().
    Même format que le jeu desktop.
    """
    parties = []
    
    try:
        if db_manager.connect():
            try:
                # Récupération via la méthode du jeu desktop
                all_games = db_manager.get_all_games(order_by='id')
                
                # Inversion pour avoir les plus récentes en premier (comme ORDER BY id DESC)
                parties = list(reversed(all_games))[:50]
                
                # Enrichissement des données pour l'affichage
                for partie in parties:
                    # Déterminer le gagnant à partir du nombre de coups
                    coups = partie.get('coups', '')
                    nb_coups = len(coups)
                    
                    # Joueur 1 joue aux coups impairs (1, 3, 5...), Joueur 2 aux coups pairs (2, 4, 6...)
                    # Si victoire au coup N : gagnant = J1 si N impair, J2 si N pair
                    if partie.get('ligne_gagnante'):
                        partie['gagnant'] = 'Rouge' if nb_coups % 2 == 1 else 'Jaune'
                    else:
                        partie['gagnant'] = 'Nul'
                    
                    # Alias pour compatibilité avec le template
                    partie['historique_coups'] = coups
                    partie['date_partie'] = partie.get('created_at')
                    
            finally:
                db_manager.disconnect()
    except Exception as e:
        print(f"[HISTORIQUE ERROR] {e}")
    
    return render_template('historique.html', parties=parties)


if __name__ == '__main__':
    print("=" * 50)
    print("🎮 Puissance 4 Web PRO - Démarrage du serveur")
    print("=" * 50)
    print(f"Configuration: {ROWS} lignes x {COLS} colonnes")
    print("Routes disponibles:")
    print("  - GET  /              : Interface de jeu")
    print("  - GET  /health        : Status du serveur")
    print("  - GET  /historique    : Historique des parties")
    print("  - POST /api/get_ai_move : Obtenir un coup IA + scores")
    print("  - POST /api/check_win   : Vérifier victoire")
    print("  - POST /api/save        : Sauvegarder une partie")
    print("=" * 50)
    print("Fonctionnalités PRO activées:")
    print("  ✅ Profondeur Minimax configurable (1-6)")
    print("  ✅ Scores Minimax en direct par colonne")
    print("  ✅ Pause/Reprendre la partie")
    print("  ✅ Sauvegarde BDD (AlwaysData)")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)