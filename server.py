import socket
import threading
import uuid

HOST = 'localhost'
PORT = 21019

lobby = []
active_games = {}
lock = threading.Lock()

def check_win(board):
    combos = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a, b, c in combos:
        if board[a] == board[b] == board[c] != '-':
            return True
    return False

def board_string(board):
    return ''.join(board)

def send_to_players(players, message):
    for p in players:
        if p:
            try:
                p.sendall(message.encode())
            except:
                continue

def game_thread(game_id):
    with lock:
        board, players, current_turn = active_games[game_id]

    print(f"[Game {game_id}] Started.")
    send_to_players(players, f"GAME_ID {game_id}\n")

    for i, conn in enumerate(players):
        if conn:
            conn.sendall(f"WELCOME {i+1}\n".encode())
            conn.sendall(b"START\n")
            conn.sendall(f"BOARD {board_string(board)}\n".encode())

    def send_turn():
        if players[current_turn]:
            players[current_turn].sendall(b"YOUR_TURN\n")
        if players[1 - current_turn]:
            players[1 - current_turn].sendall(b"WAIT\n")

    send_turn()

    while True:
        conn = players[current_turn]
        if not conn:
            current_turn = 1 - current_turn
            continue
        try:
            data = conn.recv(1024)
            if not data:
                raise ConnectionResetError()
            message = data.decode().strip()

            if message == "QUIT":
                print(f"[Game {game_id}] Player {current_turn} quit.")
                other = players[1 - current_turn]
                if other:
                    other.sendall(b"OPPONENT_LEFT\n")
                    with lock:
                        lobby.append(other)
                break

            if message.startswith("MOVE"):
                parts = message.split()
                if len(parts) != 2 or not parts[1].isdigit():
                    conn.sendall(b"INVALID\nYOUR_TURN\n")
                    continue
                cell = int(parts[1])
                if cell < 0 or cell > 8 or board[cell] != '-':
                    conn.sendall(b"INVALID\nYOUR_TURN\n")
                    continue

                board[cell] = 'X' if current_turn == 0 else 'O'
                conn.sendall(b"VALID\n")
                send_to_players(players, f"BOARD {board_string(board)}\n")
                if players[1 - current_turn]:
                    players[1 - current_turn].sendall(f"MOVE {cell}\n".encode())

                if check_win(board):
                    conn.sendall(b"WIN\n")
                    if players[1 - current_turn]:
                        players[1 - current_turn].sendall(b"LOSE\n")
                    break
                elif '-' not in board:
                    send_to_players(players, "DRAW\n")
                    break

                current_turn = 1 - current_turn
                with lock:
                    active_games[game_id] = (board, players, current_turn)
                send_turn()
        except:
            print(f"[Game {game_id}] Player {current_turn} disconnected.")
            other = players[1 - current_turn]
            if other:
                other.sendall(b"OPPONENT_LEFT\n")
                with lock:
                    lobby.append(other)
            break

    with lock:
        del active_games[game_id]
    print(f"[Game {game_id}] Ended.")

def lobby_manager():
    while True:
        with lock:
            if len(lobby) >= 2:
                player1 = lobby.pop(0)
                player2 = lobby.pop(0)
                board = ['-'] * 9
                game_id = str(uuid.uuid4())[:8]
                active_games[game_id] = (board, [player1, player2], 0)
                threading.Thread(target=game_thread, args=(game_id,), daemon=True).start()

def client_handler(conn, addr):
    print(f"Client connected from {addr}")
    conn.sendall(b"JOINED_LOBBY\n")
    with lock:
        lobby.append(conn)

def main():
    threading.Thread(target=lobby_manager, daemon=True).start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server running on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()

