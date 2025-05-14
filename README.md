# Networked Tic Tac Toe Game

This is a **multiplayer Tic Tac Toe game** built using **Python sockets** and **multithreading**. It allows multiple players to play simultaneous games over a network—whether on the same machine or from different computers and networks.

---

## 📂 Project Structure

```
.
├── server.py   # Server code that manages games, players, and matchmaking
└── client.py   # Client code that connects to server and plays the game
```

---

## Features

✅ **Multithreading**: Multiple games can run concurrently. Each pair of connected players is handled in its own thread.

✅ **Automatic Matchmaking**: Players are placed in a lobby and automatically matched into games as soon as there are two players available.

✅ **Quit & Reconnect Logic**: If a player types `quit`, they gracefully leave the game. Their opponent remains on the server and is returned to the lobby to be matched with the next available player.

✅ **Real-Time Game Updates**: Each move is communicated between players in real time. The server keeps track of the board state and current turn.

✅ **Game Persistence**: Each game is assigned a unique ID, and board state is managed per game.

✅ **Robust Input Validation**: Invalid inputs (letters, symbols, numbers outside 0–8) are caught and do not crash the program. Players are notified and prompted to try again.

✅ **Custom Text-Based Protocol**:
- Messages are exchanged using plain text strings like `JOINED_LOBBY`, `MOVE 4`, `WIN`, `DRAW`, etc.

---

## How It Works

### Server (`server.py`)

- Listens for incoming connections on a configurable port (default: `21019`).
- Adds new clients to a lobby.
- Automatically pairs players and launches a separate game thread for each pair.
- Maintains the game state (board, turn, etc.) and validates moves.
- Handles disconnects, quitting, and re-matching seamlessly.

### Client (`client.py`)

- Connects to the server and waits in the lobby until paired.
- Receives game instructions (whose turn, board updates, win/lose notifications).
- Lets players input their moves (numbers 0–8) or type `quit` to leave the game.
- Displays a simple text-based board in the terminal.

---

## How to Play

1. **Run the Server** (on one machine):

```bash
python3 server.py
```

2. **Run the Client** (on the same or different machines):

```bash
python3 client.py
```

3. **Gameplay**:
   - Wait to be matched with another player.
   - You'll see a board displayed with positions 0–8.
   - On your turn, enter a number between `0` and `8` to place your mark.
   - The opponent will be notified of your move.
   - First to align three marks (horizontally, vertically, or diagonally) wins.
   - If the board fills without a winner, the game ends in a draw.
   - Type `quit` any time to leave the game and return your opponent to the lobby.

---

## Example Board Mapping

```
0 | 1 | 2
--+---+--
3 | 4 | 5
--+---+--
6 | 7 | 8
```

---

## 📜 Game Protocol Overview

The server communicates with clients using simple newline-delimited text commands:

- `JOINED_LOBBY`: You are in the queue waiting for an opponent.
- `WELCOME <1|2>`: You are Player 1 (X) or Player 2 (O).
- GAME_ID <id>: Unique ID assigned to your game.
- START: Game has started.
- BOARD <state>: Current board state, 9 characters (e.g., `XOX-O--X-`).
- YOUR_TURN: It's your turn to play.
- WAIT: Waiting for the other player's move.
- MOVE <pos>: Notification of opponent’s move.
- VALID: Your move was accepted.
- INVALID: Your move was invalid (e.g., cell occupied).
- WIN, LOSE, DRAW: End-of-game results.
- OPPONENT_LEFT: Opponent disconnected or quit.

---

## Example Gameplay

**server**
```
Server running on localhost:21019
```

**client1**

```
Connected to server.
Waiting for opponent...
```

**server**

```
Client connected from ('127.0.0.1', 33156)
```

**client2**

```
Connected to server.
Waiting for opponent...
Game ID: e9d7f487
WELCOME 2
Game started!
  |   |
--+---+--
  |   |
--+---+--
  |   |
Waiting for opponent's move...
```

**server**

```
Client connected from ('127.0.0.1', 55708)
[Game e9d7f487] Started.
```

**client1**

```
Game ID: e9d7f487
WELCOME 1
Game started!
  |   |
--+---+--
  |   |
--+---+--
  |   |
Your move (0-8 or 'quit'): 2
Move accepted.
  |   | X
--+---+--
  |   |
--+---+--
  |   |
Waiting for opponent's move...
```

**client2**

```
  |   | X
--+---+--
  |   |
--+---+--
  |   |
Opponent moved at 2
Your move (0-8 or 'quit'): 2
Invalid move. Try again.
Your move (0-8 or 'quit'): 4
Move accepted.
  |   | X
--+---+--
  | O |
--+---+--
  |   |
Waiting for opponent's move...
```

**client1**

```
  |   | X
--+---+--
  | O |
--+---+--
  |   |
Opponent moved at 4
Your move (0-8 or 'quit'): quit
```

**server**

```
[Game e9d7f487] Player 0 quit.
[Game e9d7f487] Ended.
```

**client2**

```
Your opponent left. You will be matched with a new one.
```

**client3**

```
Connected to server.
Waiting for opponent...
Game ID: 786e5b2f
WELCOME 2
Game started!
  |   |
--+---+--
  |   |
--+---+--
  |   |
Waiting for opponent's move...
```

**server**

```
Client connected from ('127.0.0.1', 52162)
[Game 786e5b2f] Started.
```

**client2**

```
Game ID: 786e5b2f
WELCOME 1
Game started!
  |   |
--+---+--
  |   |
--+---+--
  |   |
Your move (0-8 or 'quit'): 7
Move accepted.
  |   |
--+---+--
  |   |
--+---+--
  | X |
Waiting for opponent's move...
```

**client3**

```
  |   |
--+---+--
  |   |
--+---+--
  | X |
Opponent moved at 7
Your move (0-8 or 'quit'): 5
Move accepted.
  |   |
--+---+--
  |   | O
--+---+--
  | X |
Waiting for opponent's move...
```

**client2**

```
  |   |
--+---+--
  |   | O
--+---+--
  | X |
Opponent moved at 5
Your move (0-8 or 'quit'): 1
Move accepted.
  | X |
--+---+--
  |   | O
--+---+--
  | X |
Waiting for opponent's move...
```

**client3**

```
  | X |
--+---+--
  |   | O
--+---+--
  | X |
Opponent moved at 1
Your move (0-8 or 'quit'): 2
Move accepted.
  | X | O
--+---+--
  |   | O
--+---+--
  | X |
Waiting for opponent's move...
```

**client2**

```
  | X | O
--+---+--
  |   | O
--+---+--
  | X |
Opponent moved at 2
Your move (0-8 or 'quit'): 4
Move accepted.
  | X | O
--+---+--
  | X | O
--+---+--
  | X |
You win!
```

**client3**

```
  | X | O
--+---+--
  | X | O
--+---+--
  | X |
Opponent moved at 4
You lose!
```

**server**

```
[Game 786e5b2f] Ended.
```

---

## Error Handling

- If you enter a non-numeric value like `a`, `!`, or `hello`, you'll see:
  ```
  Invalid input.
  Your move (0-8 or 'quit'):
  ```

- If you enter a number out of range (e.g., `10`), you'll see:
  ```
  Invalid move. Try again.
  Your move (0-8 or 'quit'):
  ```

- If you try to play in an already taken cell, you'll also get prompted to try again.

---

## Notes

- You can run the server and clients on different machines across a local network or over the internet (with port forwarding).
- The server supports as many simultaneous games as your machine can handle.

---

## Requirements

- Python 3.x

No external libraries are required.

---

