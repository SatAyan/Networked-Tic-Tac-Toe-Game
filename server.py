import socket
import threading

HOST = 'localhost'
PORT = 21019

# Use '-' instead of space to represent empty cells
board = ['-'] * 9
players = []
player_sockets = [None, None]
current_turn = 0
game_started = False
lock = threading.Lock()

def check_win():
    combos = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a, b, c in combos:
        if board[a] == board[b] == board[c] != '-':
            return True
    return False

def board_string():
    return ''.join(board)

def broadcast(msg):
    for sock in player_sockets:
        if sock:
            sock.sendall(f"{msg}\n".encode())

def handle_client(conn, player_id):
    global current_turn, game_started
    conn.sendall(f"WELCOME {player_id+1}\n".encode())

    if len(players) == 2:
        game_started = True
        broadcast("START")
        broadcast(f"BOARD {board_string()}")
        player_sockets[current_turn].sendall(b"YOUR_TURN\n")
        player_sockets[1 - current_turn].sendall(b"WAIT\n")

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode().strip()

            if message.startswith("MOVE"):
                _, cell = message.split()
                cell = int(cell)
                if cell > 8 or cell < 0:
                    conn.sendall(b"INVALID\n")
                    conn.sendall(b"YOUR_TURN\n")
                    continue

                with lock:
                    if player_id != current_turn:
                        conn.sendall(b"WAIT\n")
                        continue

                    if board[cell] != '-':
                        conn.sendall(b"INVALID\n")
                        conn.sendall(b"YOUR_TURN\n")
                        continue

                    board[cell] = 'X' if player_id == 0 else 'O'
                    conn.sendall(b"VALID\n")
                    broadcast(f"BOARD {board_string()}")
                    opponent = 1 - player_id
                    player_sockets[opponent].sendall(f"MOVE {cell}\n".encode())

                    if check_win():
                        conn.sendall(b"WIN\n")
                        player_sockets[opponent].sendall(b"LOSE\n")
                        break
                    elif '-' not in board:
                        broadcast("DRAW")
                        break

                    current_turn = opponent
                    player_sockets[current_turn].sendall(b"YOUR_TURN\n")
                    player_sockets[1 - current_turn].sendall(b"WAIT\n")

            elif message == "QUIT":
                broadcast("BYE")
                break

        except Exception as e:
            print(f"Error: {e}")
            break

    conn.close()

def main():
    global players
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server running on {HOST}:{PORT}")

        while len(players) < 2:
            conn, addr = s.accept()
            print(f"Player connected from {addr}")
            players.append(conn)
            player_id = len(players) - 1
            player_sockets[player_id] = conn
            threading.Thread(target=handle_client, args=(conn, player_id)).start()

if __name__ == "__main__":
    main()
