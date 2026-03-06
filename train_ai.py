"""
Entraine une IA RandomForest pour Puissance 4 (9 colonnes) a partir des parties en base.

Objectif:
- Ne plus utiliser Minimax en production.
- Entrainer un modele statistique sur l'historique de la BDD.

Sortie:
- ai_model.joblib
"""

from __future__ import annotations

import argparse
import os
from typing import List, Optional, Tuple

import joblib
import mysql.connector
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ROWS = 8
COLS = 9
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2
WIN_LENGTH = 4
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


def create_board(rows: int = ROWS, cols: int = COLS) -> np.ndarray:
    return np.zeros((rows, cols), dtype=np.int8)


def get_next_open_row(board: np.ndarray, col: int) -> Optional[int]:
    for row in range(board.shape[0]):
        if board[row, col] == EMPTY:
            return row
    return None


def drop_piece(board: np.ndarray, col: int, piece: int) -> Optional[int]:
    row = get_next_open_row(board, col)
    if row is None:
        return None
    board[row, col] = piece
    return row


def check_win(board: np.ndarray, piece: int) -> bool:
    rows, cols = board.shape
    for row in range(rows):
        for col in range(cols):
            if board[row, col] != piece:
                continue
            for dy, dx in DIRECTIONS:
                ok = True
                for i in range(WIN_LENGTH):
                    r = row + i * dy
                    c = col + i * dx
                    if r < 0 or r >= rows or c < 0 or c >= cols or board[r, c] != piece:
                        ok = False
                        break
                if ok:
                    return True
    return False


def parse_coups_base1(coups: str, cols: int = COLS) -> List[int]:
    """Convertit une chaine de coups base1 ('455213...') en colonnes base0."""
    moves: List[int] = []
    for ch in coups:
        if not ch.isdigit():
            continue
        col = int(ch) - 1
        if 0 <= col < cols:
            moves.append(col)
    return moves


def infer_winner_and_samples(coups: str, rows: int = ROWS, cols: int = COLS) -> Tuple[Optional[int], List[np.ndarray], List[int]]:
    """
    Reconstruit une partie et retourne:
    - le gagnant (1/2) ou None
    - les features X pour les tours du gagnant
    - les labels y (colonne jouee par le gagnant)

    Features: plateau encode du point de vue du joueur courant
    (1 = mes pions, -1 = adversaire, 0 = vide)
    """
    moves = parse_coups_base1(coups, cols=cols)
    if not moves:
        return None, [], []

    board = create_board(rows, cols)
    current_player = PLAYER1
    winner: Optional[int] = None

    # Premier passage: determiner le gagnant
    for col in moves:
        if drop_piece(board, col, current_player) is None:
            return None, [], []
        if check_win(board, current_player):
            winner = current_player
            break
        current_player = PLAYER1 if current_player == PLAYER2 else PLAYER2

    if winner is None:
        return None, [], []

    # Deuxieme passage: extraire echantillons du gagnant
    board = create_board(rows, cols)
    current_player = PLAYER1
    x_samples: List[np.ndarray] = []
    y_samples: List[int] = []

    for col in moves:
        if current_player == winner:
            opponent = PLAYER1 if current_player == PLAYER2 else PLAYER2
            encoded = np.where(board == current_player, 1, np.where(board == opponent, -1, 0)).astype(np.int8)
            x_samples.append(encoded.flatten())
            y_samples.append(col)

        if drop_piece(board, col, current_player) is None:
            return winner, x_samples, y_samples

        if check_win(board, current_player):
            break

        current_player = PLAYER1 if current_player == PLAYER2 else PLAYER2

    return winner, x_samples, y_samples


def load_games_from_db(host: str, user: str, password: str, database: str, port: int, table: str, limit: int = 0) -> List[str]:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        connect_timeout=10,
    )
    try:
        cursor = conn.cursor()
        query = f"SELECT coups FROM {table} WHERE coups IS NOT NULL AND coups <> ''"
        if limit > 0:
            query += f" ORDER BY id DESC LIMIT {int(limit)}"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [str(r[0]) for r in rows if r and r[0]]
    finally:
        conn.close()


def build_dataset(coups_list: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    x_all: List[np.ndarray] = []
    y_all: List[int] = []

    for coups in coups_list:
        _, xs, ys = infer_winner_and_samples(coups)
        if xs and ys:
            x_all.extend(xs)
            y_all.extend(ys)

    if not x_all:
        return np.empty((0, ROWS * COLS), dtype=np.int8), np.empty((0,), dtype=np.int8)

    return np.array(x_all, dtype=np.int8), np.array(y_all, dtype=np.int8)


def train_model(x: np.ndarray, y: np.ndarray) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=400,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced_subsample",
        min_samples_leaf=1,
    )
    model.fit(x, y)
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrainement du modele IA (RandomForest) depuis la BDD.")
    parser.add_argument(
        "--db-host",
        default=os.getenv("TRAIN_DB_HOST") or os.getenv("DB_HOST", "mysql-metuscarnel.alwaysdata.net"),
    )
    parser.add_argument(
        "--db-user",
        default=os.getenv("TRAIN_DB_USER") or os.getenv("DB_USER", "metuscarnel"),
    )
    parser.add_argument(
        "--db-password",
        default=(
            os.getenv("TRAIN_DB_PASS")
            or os.getenv("DB_PASS")
            or os.getenv("DB_PASSWORD", "$Maestro137#")
        ),
    )
    parser.add_argument(
        "--db-name",
        default=os.getenv("TRAIN_DB_NAME") or os.getenv("DB_NAME", "metuscarnel_connect4"),
    )
    parser.add_argument(
        "--db-port",
        type=int,
        default=int(os.getenv("TRAIN_DB_PORT") or os.getenv("DB_PORT", "3306")),
    )
    parser.add_argument("--table", default=os.getenv("TRAIN_DB_TABLE", "games"))
    parser.add_argument("--limit", type=int, default=0, help="Limiter le nombre de parties chargees (0 = toutes)")
    parser.add_argument("--model-path", default=os.path.join(os.path.dirname(__file__), "ai_model.joblib"))
    args = parser.parse_args()

    print("[TRAIN] Chargement des parties depuis la base...")
    coups_list = load_games_from_db(
        host=args.db_host,
        user=args.db_user,
        password=args.db_password,
        database=args.db_name,
        port=args.db_port,
        table=args.table,
        limit=args.limit,
    )
    print(f"[TRAIN] Parties chargees: {len(coups_list)}")

    x, y = build_dataset(coups_list)
    print(f"[TRAIN] Echantillons exploites: {len(y)}")

    if len(y) < 20:
        raise RuntimeError("Pas assez de donnees pour entrainer un modele fiable (minimum recommande: 20 echantillons).")

    unique_classes = np.unique(y)
    if unique_classes.shape[0] < 2:
        raise RuntimeError("Dataset insuffisant: au moins 2 colonnes cibles differentes sont requises.")

    # Evaluation simple hold-out
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    model = train_model(x_train, y_train)
    y_pred = model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[TRAIN] Accuracy (hold-out): {acc:.4f}")

    # Refit sur tout le dataset pour la prod
    model = train_model(x, y)
    joblib.dump(model, args.model_path)
    print(f"[TRAIN] Modele enregistre: {args.model_path}")
    print(f"[TRAIN] Features attendues: {model.n_features_in_}")


if __name__ == "__main__":
    main()
