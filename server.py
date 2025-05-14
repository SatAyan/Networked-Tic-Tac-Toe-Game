import socket
import threading

HOST = 'localhost'
PORT = 21019

lobby = []
lock = threading.Lock()

def check_win(board):
    combos = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a, b, c in combos:
        if board[a] == board[b] == board[c] != '-':
            return True
    return False

def board_string(board):
    return ''.join(board)

def game_thread(player_sockets, game_id):
    board = ['-'] * 9
    current_turn = 0
    print(f"[Game {game_id}] Started.")

    for i, conn in enumerate(player_sockets):
        conn.sendall(f"WELCOME {i+1}\n".encode())
    for conn in player_sockets:
        conn.sendall(b"START\n")
        conn.sendall(f"BOARD {board_string(board)}\n".encode())

    player_sockets[current_turn].sendall(b"YOUR_TURN\n")
    player_sockets[1 - current_turn].sendall(b"WAIT\n")

    while True:
        try:
            conn = player_sockets[current_turn]
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode().strip()

            if message.startswith("MOVE"):
                parts = message.split()
                if len(parts) != 2 or not parts[1].isdigit():
                    conn.sendall(b"INVALID\nYOUR_TURN\n")
                    continue

                cell = int(parts[1])
                if cell < 0 or cell > 8:
                    conn.sendall(b"INVALID\nYOUR_TURN\n")
                    continue

                if board[cell] != '-':
                    conn.sendall(b"INVALID\nYOUR_TURN\n")
                    continue

                board[cell] = 'X' if current_turn == 0 else 'O'
                conn.sendall(b"VALID\n")
                for sock in player_sockets:
                    sock.sendall(f"BOARD {board_string(board)}\n".encode())
                player_sockets[1 - current_turn].sendall(f"MOVE {cell}\n".encode())

                if check_win(board):
                    conn.sendall(b"WIN\n")
                    player_sockets[1 - current_turn].sendall(b"LOSE\n")
                    break
                elif '-' not in board:
                    for sock in player_sockets:
                        sock.sendall(b"DRAW\n")
                    break

                current_turn = 1 - current_turn
                player_sockets[current_turn].sendall(b"YOUR_TURN\n")
                player_sockets[1 - current_turn].sendall(b"WAIT\n")

            elif message == "QUIT":
                for sock in player_sockets:
                    sock.sendall(b"BYE\n")
                break

        except Exception as e:
            print(f"[Game {game_id}] Error: {e}")
            break

    for conn in player_sockets:
        conn.close()
    print(f"[Game {game_id}] Ended.")

def lobby_manager():
    game_id = 1
    while True:
        with lock:
            if len(lobby) >= 2:
                player1 = lobby.pop(0)
                player2 = lobby.pop(0)
                threading.Thread(target=game_thread, args=([player1, player2], game_id)).start()
                game_id += 1

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
