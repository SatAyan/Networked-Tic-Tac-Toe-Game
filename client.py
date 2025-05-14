import socket

HOST = 'localhost'
PORT = 21019

def print_board(state):
    state = state.replace('-', ' ')
    state = state.ljust(9)
    print(f"{state[0]} | {state[1]} | {state[2]}")
    print("--+---+--")
    print(f"{state[3]} | {state[4]} | {state[5]}")
    print("--+---+--")
    print(f"{state[6]} | {state[7]} | {state[8]}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to server.")

        while True:
            data = s.recv(1024).decode()
            if not data:
                break

            for line in data.strip().split('\n'):
                if line == "JOINED_LOBBY":
                    print("Waiting for opponent...")
                elif line.startswith("WELCOME"):
                    print(line)
                elif line.startswith("GAME_ID"):
                    print(f"Game ID: {line.split()[1]}")
                elif line == "START":
                    print("Game started!")
                elif line.startswith("BOARD"):
                    _, board = line.split()
                    print_board(board)
                elif line == "YOUR_TURN":
                    while True:
                        move = input("Your move (0-8 or 'quit'): ").strip()
                        if move.lower() == "quit":
                            s.sendall(b"QUIT\n")
                            return
                        if move.isdigit() and 0 <= int(move) <= 8:
                            s.sendall(f"MOVE {move}\n".encode())
                            break
                        print("Invalid input.")
                elif line == "WAIT":
                    print("Waiting for opponent's move...")
                elif line == "VALID":
                    print("Move accepted.")
                elif line == "INVALID":
                    print("Invalid move. Try again.")
                elif line.startswith("MOVE"):
                    _, pos = line.split()
                    print(f"Opponent moved at {pos}")
                elif line == "WIN":
                    print("You win!")
                    return
                elif line == "LOSE":
                    print("You lose!")
                    return
                elif line == "DRAW":
                    print("It's a draw!")
                    return
                elif line == "OPPONENT_LEFT":
                    print("Your opponent left. You will be matched with a new one.")
                    break

if __name__ == "__main__":
    main()

