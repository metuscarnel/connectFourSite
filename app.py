"""
Application Flask AUTONOME pour le jeu Puissance 4 Web.
Version 100% déployable sur Render - AUCUNE dépendance externe src/.

Intègre directement :
- Constantes du jeu (ROWS, COLS, WIN_LENGTH...)
- Classe Board (plateau de jeu)
- Classe MinimaxAI (IA intelligente)
- Classe RandomAI (IA aléatoire)
- Classe DatabaseManager (connexion MySQL)

PRO Features : BDD, Pause, Profondeur configurable, Scores Minimax en temps réel.
"""

import os
import random
import json
from typing import Optional, Tuple, List
from copy import deepcopy
from flask import Flask, render_template, request, jsonify
import numpy as np
import joblib

# ============================================================
# CONSTANTES DU JEU (intégrées depuis src/utils/constants.py)
# ============================================================
ROWS: int = 8   # Nombre de lignes
COLS: int = 9   # Nombre de colonnes
EMPTY: int = 0  # Cellule vide
PLAYER1: int = 1  # Joueur 1 (Rouge)
PLAYER2: int = 2  # Joueur 2 (Jaune)
WIN_LENGTH: int = 4  # Pions alignés pour gagner

# Directions de vérification victoire (dy, dx)
DIRECTIONS: List[Tuple[int, int]] = [
    (0, 1),   # Horizontale →
    (1, 0),   # Verticale ↓
    (1, 1),   # Diagonale \
    (1, -1),  # Diagonale /
]


# ============================================================
# CLASSE BOARD (intégrée depuis src/models/board.py)
# ============================================================
class Board:
    """
    Plateau de jeu Puissance 4.
    Convention : grid[0] = bas du plateau, grid[rows-1] = haut.
    """
    
    def __init__(self, rows: int = ROWS, cols: int = COLS) -> None:
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=np.int_)
        self.history: List[Tuple[int, int]] = []
    
    def is_valid_location(self, col: int) -> bool:
        """Vérifie si une colonne peut accueillir un pion."""
        if col < 0 or col >= self.cols:
            return False
        return self.grid[self.rows - 1][col] == EMPTY
    
    def get_next_open_row(self, col: int) -> Optional[int]:
        """Trouve la première ligne vide dans une colonne (gravité)."""
        for row in range(self.rows):
            if self.grid[row][col] == EMPTY:
                return row
        return None
    
    def drop_piece(self, row: int, col: int, piece: int) -> None:
        """Place un pion dans la grille."""
        self.history.append((row, col))
        self.grid[row][col] = piece
    
    def check_win(self, piece: int) -> bool:
        """Vérifie si le joueur a gagné."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == piece:
                    for dy, dx in DIRECTIONS:
                        if self._check_direction(row, col, dy, dx, piece):
                            return True
        return False
    
    def _check_direction(self, start_row: int, start_col: int, dy: int, dx: int, piece: int) -> bool:
        """Vérifie l'alignement dans une direction."""
        for i in range(WIN_LENGTH):
            row = start_row + i * dy
            col = start_col + i * dx
            if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
                return False
            if self.grid[row][col] != piece:
                return False
        return True
    
    def get_winning_positions(self, piece: int) -> List[Tuple[int, int]]:
        """Retourne les coordonnées des pions gagnants."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == piece:
                    for dy, dx in DIRECTIONS:
                        positions = self._get_positions_in_direction(row, col, dy, dx, piece)
                        if positions:
                            return positions
        return []
    
    def _get_positions_in_direction(self, start_row: int, start_col: int, dy: int, dx: int, piece: int) -> List[Tuple[int, int]]:
        """Collecte les positions d'un alignement gagnant."""
        positions = []
        for i in range(WIN_LENGTH):
            row = start_row + i * dy
            col = start_col + i * dx
            if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
                return []
            if self.grid[row][col] == piece:
                positions.append((row, col))
            else:
                return []
        return positions if len(positions) == WIN_LENGTH else []
    
    def is_full(self) -> bool:
        """Vérifie si le plateau est plein (égalité)."""
        return not (self.grid == EMPTY).any()
    
    def get_valid_locations(self) -> List[int]:
        """Retourne les colonnes jouables."""
        return [col for col in range(self.cols) if self.is_valid_location(col)]
    
    def copy(self) -> 'Board':
        """Crée une copie du plateau."""
        new_board = Board(rows=self.rows, cols=self.cols)
        new_board.grid = np.copy(self.grid)
        new_board.history = self.history.copy()
        return new_board


# ============================================================
# CLASSE MINIMAX AI (intégrée depuis src/ai/minimax_ai.py)
# ============================================================
class MinimaxAI:
    """IA Minimax avec élagage Alpha-Beta."""
    
    def __init__(self, depth: int = 4, name: str = "Minimax AI") -> None:
        self.depth = depth
        self.name = name
        self.piece = PLAYER2
        self.opponent_piece = PLAYER1
        self.last_scores: dict = {}
    
    def set_player(self, piece: int) -> None:
        """Configure le joueur que l'IA contrôle."""
        self.piece = piece
        self.opponent_piece = PLAYER1 if piece == PLAYER2 else PLAYER2
    
    def evaluate_window(self, window: list, piece: int) -> int:
        """Évalue une fenêtre de 4 cases."""
        score = 0
        opponent = self.opponent_piece
        
        piece_count = window.count(piece)
        empty_count = window.count(EMPTY)
        opponent_count = window.count(opponent)
        
        if piece_count == 4:
            score += 100
        elif piece_count == 3 and empty_count == 1:
            score += 5
        elif piece_count == 2 and empty_count == 2:
            score += 2
        
        if opponent_count == 3 and empty_count == 1:
            score -= 4
        
        return score
    
    def score_position(self, board: Board, piece: int) -> int:
        """Évalue l'état global du plateau."""
        score = 0
        rows = board.rows
        cols = board.cols
        
        # Bonus centre
        center_col = cols // 2
        center_array = [int(board.grid[row][center_col]) for row in range(rows)]
        score += center_array.count(piece) * 3
        
        # Horizontale
        for row in range(rows):
            row_array = [int(board.grid[row][col]) for col in range(cols)]
            for col in range(cols - 3):
                window = row_array[col:col + WIN_LENGTH]
                score += self.evaluate_window(window, piece)
        
        # Verticale
        for col in range(cols):
            col_array = [int(board.grid[row][col]) for row in range(rows)]
            for row in range(rows - 3):
                window = col_array[row:row + WIN_LENGTH]
                score += self.evaluate_window(window, piece)
        
        # Diagonale /
        for row in range(rows - 3):
            for col in range(cols - 3):
                window = [board.grid[row + i][col + i] for i in range(WIN_LENGTH)]
                score += self.evaluate_window(window, piece)
        
        # Diagonale \
        for row in range(3, rows):
            for col in range(cols - 3):
                window = [board.grid[row - i][col + i] for i in range(WIN_LENGTH)]
                score += self.evaluate_window(window, piece)
        
        return score
    
    def is_terminal_node(self, board: Board) -> bool:
        """Vérifie si un nœud est terminal."""
        return (board.check_win(self.piece) or 
                board.check_win(self.opponent_piece) or 
                board.is_full())
    
    def minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool) -> Tuple[Optional[int], float]:
        """Algorithme Minimax avec Alpha-Beta."""
        valid_locations = board.get_valid_locations()
        is_terminal = self.is_terminal_node(board)
        
        if depth == 0 or is_terminal:
            if is_terminal:
                if board.check_win(self.piece):
                    return (None, 100000)
                elif board.check_win(self.opponent_piece):
                    return (None, -100000)
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(board, self.piece))
        
        if maximizing:
            value = float('-inf')
            column = random.choice(valid_locations) if valid_locations else None
            
            for col in valid_locations:
                row = board.get_next_open_row(col)
                if row is None:
                    continue
                temp_board = board.copy()
                temp_board.drop_piece(row, col, self.piece)
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, False)[1]
                
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
        else:
            value = float('inf')
            column = random.choice(valid_locations) if valid_locations else None
            
            for col in valid_locations:
                row = board.get_next_open_row(col)
                if row is None:
                    continue
                temp_board = board.copy()
                temp_board.drop_piece(row, col, self.opponent_piece)
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, True)[1]
                
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
    
    def get_move(self, board: Board) -> Optional[int]:
        """Retourne le meilleur coup."""
        self.last_scores = {}
        valid_locations = board.get_valid_locations()
        
        if not valid_locations:
            return None
        
        # Victoire immédiate
        for col in valid_locations:
            row = board.get_next_open_row(col)
            if row is not None:
                temp = board.copy()
                temp.drop_piece(row, col, self.piece)
                if temp.check_win(self.piece):
                    return col
        
        # Blocage immédiat
        for col in valid_locations:
            row = board.get_next_open_row(col)
            if row is not None:
                temp = board.copy()
                temp.drop_piece(row, col, self.opponent_piece)
                if temp.check_win(self.opponent_piece):
                    return col
        
        # Minimax
        column, _ = self.minimax(board, self.depth, float('-inf'), float('inf'), True)
        return column


# ============================================================
# CLASSE RANDOM AI (intégrée depuis src/ai/random_ai.py)
# ============================================================
class RandomAI:
    """IA aléatoire (baseline)."""
    
    def __init__(self, name: str = "Robot Aléatoire") -> None:
        self.name = name
    
    def get_move(self, board: Board) -> Optional[int]:
        """Choisit une colonne au hasard."""
        valid = board.get_valid_locations()
        return random.choice(valid) if valid else None


# ============================================================
# IA HYBRIDE (réflexe logique + modèle ML)
# ============================================================
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ai_model.joblib')
ml_model = None


def load_ml_model():
    """Charge le modèle ML depuis le disque (cache mémoire)."""
    global ml_model
    if ml_model is not None:
        return ml_model

    if not os.path.exists(MODEL_PATH):
        print(f"[ML] ⚠️ Modèle introuvable: {MODEL_PATH}")
        return None

    try:
        ml_model = joblib.load(MODEL_PATH)
        print(f"[ML] ✅ Modèle chargé: {MODEL_PATH}")
        return ml_model
    except Exception as e:
        print(f"[ML ERROR] Chargement modèle impossible: {e}")
        return None


def board_to_ml_features(board: Board, player: int) -> np.ndarray:
    """
    Encode le plateau pour le modèle.
    Vue relative au joueur courant: 1 = mes pions, -1 = adversaire, 0 = vide.
    """
    opponent = PLAYER1 if player == PLAYER2 else PLAYER2
    mapped = np.where(
        board.grid == player,
        1,
        np.where(board.grid == opponent, -1, 0)
    )
    return mapped.astype(np.int8).flatten()


def check_mandatory_moves(board: Board, player: int) -> Optional[int]:
    """Retourne un coup vital: gagner maintenant ou bloquer l'adversaire."""
    valid_locations = board.get_valid_locations()
    if not valid_locations:
        return None

    opponent = PLAYER1 if player == PLAYER2 else PLAYER2

    # 1) Coup gagnant immédiat
    for col in valid_locations:
        row = board.get_next_open_row(col)
        if row is None:
            continue
        temp = board.copy()
        temp.drop_piece(row, col, player)
        if temp.check_win(player):
            return col

    # 2) Blocage immédiat de l'adversaire
    for col in valid_locations:
        row = board.get_next_open_row(col)
        if row is None:
            continue
        temp = board.copy()
        temp.drop_piece(row, col, opponent)
        if temp.check_win(opponent):
            return col

    return None


def predict_move_with_model(board: Board, player: int) -> Tuple[Optional[int], dict]:
    """Prédit la meilleure colonne avec le modèle ML (sans arbre Minimax)."""
    valid_locations = board.get_valid_locations()
    if not valid_locations:
        return None, {}

    model = load_ml_model()
    if model is None:
        return random_ai.get_move(board), {}

    features = board_to_ml_features(board, player)
    expected_features = getattr(model, 'n_features_in_', None)
    if expected_features is not None and features.shape[0] != expected_features:
        print(
            f"[ML WARNING] Dimensions incompatibles modèle/plateau: "
            f"{features.shape[0]} != {expected_features}"
        )
        return random_ai.get_move(board), {}

    x_input = features.reshape(1, -1)

    # Scores de colonnes (probabilités de classes)
    column_scores = {col: 0 for col in valid_locations}
    try:
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(x_input)[0]
            classes = model.classes_
            for cls, p in zip(classes, proba):
                col = int(cls)
                if col in column_scores:
                    column_scores[col] = float(p)

            best_col = max(column_scores, key=column_scores.get)
            return best_col, column_scores

        pred_col = int(model.predict(x_input)[0])
        if pred_col in valid_locations:
            return pred_col, column_scores
        return random_ai.get_move(board), column_scores
    except Exception as e:
        print(f"[ML ERROR] Prédiction impossible: {e}")
        return random_ai.get_move(board), {}


def predict_move_with_minimax(board: Board, player: int, depth: int) -> Tuple[Optional[int], dict]:
    """Prédit la meilleure colonne avec Minimax (calcul d'arbre local)."""
    valid_locations = board.get_valid_locations()
    if not valid_locations:
        return None, {}

    minimax_ai.depth = max(1, int(depth))
    minimax_ai.set_player(player)

    best_score = float('-inf')
    best_column = valid_locations[0]
    column_scores: dict = {}

    for col in valid_locations:
        row = board.get_next_open_row(col)
        if row is None:
            continue

        temp_board = board.copy()
        temp_board.drop_piece(row, col, player)

        if temp_board.check_win(player):
            score = 100000
        else:
            _, score = minimax_ai.minimax(
                temp_board,
                minimax_ai.depth - 1,
                float('-inf'),
                float('inf'),
                False,
            )

        score = int(score)
        column_scores[col] = score
        if score > best_score:
            best_score = score
            best_column = col

    return best_column, column_scores


# ============================================================
# CONFIGURATION BASE DE DONNÉES (variables d'environnement)
# ============================================================
# Valeurs par défaut pour le développement local
DB_HOST = os.getenv('DB_HOST', 'mysql-metuscarnel.alwaysdata.net')
DB_USER = os.getenv('DB_USER', 'metuscarnel')
# Supporte DB_PASS (Render) OU DB_PASSWORD (legacy)
DB_PASS = os.getenv('DB_PASS') or os.getenv('DB_PASSWORD', '$Maestro137#')
DB_NAME = os.getenv('DB_NAME', 'metuscarnel_connect4')
DB_PORT = int(os.getenv('DB_PORT', '3306'))

# Détection source des variables (env ou défaut)
def _get_var_source(var_name, default):
    return '✅ ENV' if os.getenv(var_name) else '⚠️ DEFAULT'

# Log de configuration au démarrage (sans mot de passe !)
print(f"\n{'='*50}")
print("📊 Configuration Base de Données:")
print(f"   Hôte: {DB_HOST} [{_get_var_source('DB_HOST', 'mysql-metuscarnel.alwaysdata.net')}]")
print(f"   User: {DB_USER} [{_get_var_source('DB_USER', '')}]")
print(f"   Pass: {'*' * len(DB_PASS)} [{_get_var_source('DB_PASS', '') if os.getenv('DB_PASS') else _get_var_source('DB_PASSWORD', '')}]")
print(f"   Base: {DB_NAME} [{_get_var_source('DB_NAME', '')}]")
print(f"   Port: {DB_PORT}")
print(f"{'='*50}\n")


# ============================================================
# CLASSE DATABASE MANAGER
# ============================================================
class DatabaseManager:
    """Gestionnaire de connexion MySQL pour AlwaysData."""
    
    def __init__(self):
        self.connection = None
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASS
        self.database = DB_NAME
        self.port = DB_PORT
    
    def connect(self) -> bool:
        """Établit la connexion à la base de données."""
        print(f"[DB] Tentative de connexion à l'hôte: {self.host}...")
        try:
            import mysql.connector
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connect_timeout=10
            )
            print(f"[DB] ✅ Connexion réussie à {self.database}")
            return True
        except Exception as e:
            print(f"[DB ERROR] ❌ Connexion échouée: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_tables(self):
        """Crée la table games si elle n'existe pas."""
        if not self.connection:
            return
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INT AUTO_INCREMENT PRIMARY KEY,
                coups VARCHAR(255) NOT NULL,
                mode_jeu VARCHAR(50),
                statut VARCHAR(50),
                ligne_gagnante TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
        cursor.close()
    
    def insert_game(self, coups: str, mode_jeu: str = "Web", statut: str = "TERMINEE", ligne_gagnante: str = None) -> Optional[int]:
        """Insère une partie et retourne son ID (None si doublon)."""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor()
        
        # Vérification doublon (coups identiques ou symétrie miroir)
        coups_sym = ''.join(str(10 - int(c)) for c in coups)
        cursor.execute(
            "SELECT id FROM games WHERE coups = %s OR coups = %s",
            (coups, coups_sym)
        )
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            return None  # Doublon
        
        cursor.execute(
            "INSERT INTO games (coups, coups_symetrique, mode_jeu, statut, ligne_gagnante) VALUES (%s, %s, %s, %s, %s)",
            (coups, coups_sym, mode_jeu, statut, ligne_gagnante)
        )
        self.connection.commit()
        game_id = cursor.lastrowid
        cursor.close()
        return game_id
    
    def get_all_games(self, order_by: str = 'id') -> List[dict]:
        """Récupère toutes les parties."""
        if not self.connection:
            return []
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM games ORDER BY {order_by}")
        results = cursor.fetchall()
        cursor.close()
        return results
    
    def get_game_by_id(self, game_id: int) -> Optional[dict]:
        """Récupère une partie par son ID."""
        if not self.connection:
            return None
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
        result = cursor.fetchone()
        cursor.close()
        return result


# ============================================================
# APPLICATION FLASK
# ============================================================
app = Flask(__name__)

# Instances globales
db_manager = DatabaseManager()
random_ai = RandomAI(name="Random Web")
minimax_ai = MinimaxAI(depth=4, name="Minimax Web")


def init_db():
    """
    Initialise la base de données au démarrage.
    Crée la table 'games' si elle n'existe pas.
    """
    print("[DB] Initialisation de la base de données...")
    if db_manager.connect():
        try:
            db_manager.create_tables()
            print("[DB] ✅ Table 'games' vérifiée/créée")
        finally:
            db_manager.disconnect()
    else:
        print("[DB] ⚠️ Initialisation BDD échouée - L'app continue sans BDD")


@app.route('/')
def index():
    """Page d'accueil avec le jeu."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Endpoint de santé."""
    return jsonify({"status": "ok", "message": "Puissance 4 Web est opérationnel!"})


@app.route('/health/db')
def health_db():
    """
    Endpoint de diagnostic pour la connexion BDD.
    Affiche la configuration (sans mot de passe) et teste la connexion.
    """
    config = {
        "host": DB_HOST,
        "user": DB_USER,
        "database": DB_NAME,
        "port": DB_PORT,
        "password_length": len(DB_PASS),
        "env_vars": {
            "DB_HOST": '✅ SET' if os.getenv('DB_HOST') else '❌ NOT SET',
            "DB_USER": '✅ SET' if os.getenv('DB_USER') else '❌ NOT SET',
            "DB_PASS": '✅ SET' if os.getenv('DB_PASS') else '❌ NOT SET',
            "DB_PASSWORD": '✅ SET' if os.getenv('DB_PASSWORD') else '❌ NOT SET',
            "DB_NAME": '✅ SET' if os.getenv('DB_NAME') else '❌ NOT SET',
        }
    }
    
    # Test de connexion
    try:
        if db_manager.connect():
            cursor = db_manager.connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM games')
            count = cursor.fetchone()[0]
            cursor.close()
            db_manager.disconnect()
            config["connection"] = f"✅ OK - {count} parties"
        else:
            config["connection"] = "❌ FAILED"
    except Exception as e:
        config["connection"] = f"❌ ERROR: {str(e)}"
    
    return jsonify(config)


@app.route('/api/get_ai_move', methods=['POST'])
def get_ai_move():
    """API IA: Minimax ou ML, avec réflexes obligatoires (gain/blocage)."""
    try:
        data = request.get_json()
        grid_data = data.get('grid')
        ai_type = data.get('ai_type', 'minimax')
        player = data.get('player', PLAYER2)
        depth = data.get('depth', 4)
        
        if grid_data is None:
            return jsonify({"success": False, "error": "Grille manquante"}), 400
        
        rows = len(grid_data)
        cols = len(grid_data[0]) if rows > 0 else 0
        
        board = Board(rows=rows, cols=cols)
        
        # Conversion grille frontend -> backend (inversion verticale)
        for r in range(rows):
            for c in range(cols):
                board.grid[rows - 1 - r][c] = grid_data[r][c]
        
        # Etape 1: réflexe obligatoire (gagner / bloquer)
        forced_column = check_mandatory_moves(board, player)
        if forced_column is not None:
            column = forced_column
            column_scores = {forced_column: 1.0}
        # Etape 2A: Minimax (arbre)
        elif ai_type == 'minimax':
            column, column_scores = predict_move_with_minimax(board, player, depth)
        # Etape 2B: IA ML (modele entrainé)
        elif ai_type == 'ml':
            column, column_scores = predict_move_with_model(board, player)
        else:
            column_scores = {}
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
    """API pour vérifier la victoire ou l'égalité."""
    try:
        data = request.get_json()
        grid_data = data.get('grid')
        
        if grid_data is None:
            return jsonify({"game_over": False, "error": "Grille manquante"}), 400
        
        rows = len(grid_data)
        cols = len(grid_data[0]) if rows > 0 else 0
        
        board = Board(rows=rows, cols=cols)
        
        for r in range(rows):
            for c in range(cols):
                board.grid[rows - 1 - r][c] = grid_data[r][c]
        
        # Victoire joueur 1
        if board.check_win(PLAYER1):
            positions = board.get_winning_positions(PLAYER1)
            winning_line = [{"row": rows - 1 - r, "col": c} for r, c in positions]
            return jsonify({
                "game_over": True,
                "winner": PLAYER1,
                "winning_line": winning_line,
                "is_draw": False
            })
        
        # Victoire joueur 2
        if board.check_win(PLAYER2):
            positions = board.get_winning_positions(PLAYER2)
            winning_line = [{"row": rows - 1 - r, "col": c} for r, c in positions]
            return jsonify({
                "game_over": True,
                "winner": PLAYER2,
                "winning_line": winning_line,
                "is_draw": False
            })
        
        # Égalité
        if board.is_full():
            return jsonify({
                "game_over": True,
                "winner": None,
                "winning_line": [],
                "is_draw": True
            })
        
        # En cours
        return jsonify({
            "game_over": False,
            "winner": None,
            "winning_line": [],
            "is_draw": False
        })
    
    except Exception as e:
        print(f"[API ERROR] check_win: {e}")
        return jsonify({"game_over": False, "error": str(e)}), 500


@app.route('/api/save', methods=['POST'])
def save_game():
    """Sauvegarde une partie terminée."""
    try:
        data = request.get_json()
        historique_coups_base0 = data.get('historique_coups', '')
        mode_jeu = data.get('mode_jeu', 'Web')
        ligne_gagnante_raw = data.get('ligne_gagnante')
        
        # Conversion Base 0 -> Base 1
        coups_base1 = ''.join(str(int(c) + 1) for c in historique_coups_base0)
        
        # Préparation ligne gagnante
        ligne_gagnante_json = None
        if ligne_gagnante_raw:
            if isinstance(ligne_gagnante_raw, str):
                ligne_gagnante = json.loads(ligne_gagnante_raw)
            else:
                ligne_gagnante = ligne_gagnante_raw
            ligne_gagnante_base1 = [(pos['row'] + 1, pos['col'] + 1) for pos in ligne_gagnante]
            ligne_gagnante_json = json.dumps(ligne_gagnante_base1)
        
        if not db_manager.connect():
            return jsonify({"success": False, "error": "Connexion BDD échouée"}), 500
        
        try:
            db_manager.create_tables()
            game_id = db_manager.insert_game(
                coups=coups_base1,
                mode_jeu=mode_jeu,
                statut="TERMINEE",
                ligne_gagnante=ligne_gagnante_json
            )
            
            if game_id is None:
                # Doublon - mise à jour ligne_gagnante
                coups_sym = ''.join(str(10 - int(c)) for c in coups_base1)
                cursor = db_manager.connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT id, ligne_gagnante FROM games WHERE coups = %s OR coups = %s LIMIT 1",
                    (coups_base1, coups_sym)
                )
                existing = cursor.fetchone()
                
                if existing and ligne_gagnante_json:
                    cursor.execute(
                        "UPDATE games SET ligne_gagnante = %s WHERE id = %s",
                        (ligne_gagnante_json, existing['id'])
                    )
                    db_manager.connection.commit()
                cursor.close()
                
                return jsonify({
                    "success": True,
                    "message": "Partie déjà existante",
                    "id": existing['id'] if existing else None,
                    "duplicate": True
                })
            
            return jsonify({
                "success": True,
                "message": "Partie sauvegardée !",
                "id": game_id
            })
        finally:
            db_manager.disconnect()
    
    except Exception as e:
        print(f"[API ERROR] save_game: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/historique')
def historique():
    """Affiche l'historique des parties."""
    parties = []
    db_error = None
    
    try:
        if db_manager.connect():
            try:
                all_games = db_manager.get_all_games(order_by='id')
                parties = list(reversed(all_games))[:50]
                
                for partie in parties:
                    coups = partie.get('coups', '')
                    nb_coups = len(coups)
                    if partie.get('ligne_gagnante'):
                        partie['gagnant'] = 'Rouge' if nb_coups % 2 == 1 else 'Jaune'
                    else:
                        partie['gagnant'] = 'Nul'
                    partie['historique_coups'] = coups
                    partie['date_partie'] = partie.get('created_at')
                print(f"[HISTORIQUE] {len(parties)} parties récupérées")
            finally:
                db_manager.disconnect()
        else:
            db_error = f"Impossible de se connecter à {DB_HOST}"
            print(f"[HISTORIQUE ERROR] {db_error}")
    except Exception as e:
        db_error = str(e)
        print(f"[HISTORIQUE ERROR] {e}")
    
    return render_template('historique.html', parties=parties, db_error=db_error)


@app.route('/replay/<int:game_id>')
def replay(game_id):
    """Lance le mode Replay pour revoir une partie."""
    moves = ""
    winning_line_base0 = None
    error = None
    
    try:
        if db_manager.connect():
            try:
                partie = db_manager.get_game_by_id(game_id)
                
                if partie:
                    coups_base1 = partie.get('coups', '')
                    moves = ''.join(str(int(c) - 1) for c in coups_base1)
                    
                    ligne_gagnante_raw = partie.get('ligne_gagnante')
                    if ligne_gagnante_raw:
                        try:
                            ligne_gagnante_base1 = json.loads(ligne_gagnante_raw) if isinstance(ligne_gagnante_raw, str) else ligne_gagnante_raw
                            winning_line_base0 = [{"row": pos[0] - 1, "col": pos[1] - 1} for pos in ligne_gagnante_base1]
                        except Exception as e:
                            print(f"[REPLAY WARNING] Erreur conversion: {e}")
                    
                    print(f"[REPLAY] Partie #{game_id}: {len(moves)} coups")
                else:
                    error = f"Partie #{game_id} introuvable"
            finally:
                db_manager.disconnect()
    except Exception as e:
        error = str(e)
        print(f"[REPLAY ERROR] {e}")
    
    return render_template('index.html', replay_mode=True, moves=moves, game_id=game_id, winning_line=winning_line_base0, error=error)


# ============================================================
# POINT D'ENTRÉE
# ============================================================
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🎮 Puissance 4 Web PRO - Serveur AUTONOME")
    print("=" * 50)
    print(f"Configuration: {ROWS} lignes x {COLS} colonnes")
    print("Routes: /, /health, /historique, /replay/<id>")
    print("APIs: /api/get_ai_move, /api/check_win, /api/save")
    print("=" * 50 + "\n")
    
    # Initialisation BDD au démarrage
    init_db()
    
    port = int(os.getenv('PORT', '5001'))
    debug_mode = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    print(f"\n🚀 Démarrage sur le port {port} (debug={debug_mode})\n")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
