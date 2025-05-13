import socket

HOST = 'localhost'
PORT = 21019

def print_board(state):
    # Replace placeholder '-' back with spaces for nicer output
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
        s.sendall(b"JOIN\n")

        while True:
            data = s.recv(1024).decode()
            if not data:
                break

            for line in data.strip().split('\n'):
                if line.startswith("WELCOME"):
                    print(line)
                elif line == "START":
                    print("Game started!")
                elif line.startswith("BOARD"):
                    parts = line.split(maxsplit=1)
                    if len(parts) == 2:
                        _, state = parts
                        print_board(state)
                elif line.startswith("YOUR_TURN"):
                    move = input("Your move (0-8): ")
                    s.sendall(f"MOVE {move}\n".encode())
                elif line.startswith("WAIT"):
                    print("Waiting for opponent...")
                elif line.startswith("VALID"):
                    print("Move accepted.")
                elif line.startswith("INVALID"):
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
                elif line == "BYE":
                    print("Game ended.")
                    return

if __name__ == "__main__":
    main()
