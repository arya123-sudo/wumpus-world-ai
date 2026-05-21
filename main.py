import tkinter as tk
from tkinter import messagebox
import random
import subprocess
import sys

# ================= SETTINGS ================= #

WINDOW_SIZE = 700
GRID_SIZE = 4
CELL_SIZE = 120

# ================= RANDOM WORLD ================= #

world = []

for i in range(GRID_SIZE):

    row = []

    for j in range(GRID_SIZE):
        row.append('')

    world.append(row)

def place_random_objects():

    placed_positions = set()

    # Safe Start
    placed_positions.add((0, 0))

    # Wumpus
    while True:

        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)

        if (x, y) not in placed_positions:

            world[x][y] = 'W'
            placed_positions.add((x, y))
            break

    # Gold
    while True:

        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)

        if (x, y) not in placed_positions:

            world[x][y] = 'G'
            placed_positions.add((x, y))
            break

    # Pits
    for _ in range(3):

        while True:

            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)

            if (x, y) not in placed_positions:

                world[x][y] = 'P'
                placed_positions.add((x, y))
                break

place_random_objects()

# ================= AGENT DATA ================= #

agent_x = 0
agent_y = 0

visited = set()
safe_cells = set()
explored = set()
dangerous_cells = set()
revealed_objects = set()

recent_moves = []

score = 0
moves = 0

# ================= GUI ================= #

root = tk.Tk()

root.title("Wumpus World AI Simulation")
root.configure(bg="#111111")
root.geometry("1150x720")

# ================= FRAMES ================= #

left_frame = tk.Frame(root, bg="#111111")
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

right_frame = tk.Frame(root, bg="#1a1a1a", width=350)
right_frame.pack(side=tk.RIGHT, fill=tk.Y)

# ================= CANVAS ================= #

canvas = tk.Canvas(
    left_frame,
    width=WINDOW_SIZE,
    height=WINDOW_SIZE,
    bg="#111111",
    highlightthickness=0
)

canvas.pack()

# ================= DASHBOARD ================= #

title_label = tk.Label(
    right_frame,
    text="WUMPUS WORLD AI",
    font=("Arial", 22, "bold"),
    bg="#1a1a1a",
    fg="cyan"
)

title_label.pack(pady=20)

status_label = tk.Label(
    right_frame,
    text="AI Starting...",
    font=("Arial", 14, "bold"),
    bg="#1a1a1a",
    fg="white"
)

status_label.pack(pady=5)

score_label = tk.Label(
    right_frame,
    text="Score: 0",
    font=("Arial", 14, "bold"),
    bg="#1a1a1a",
    fg="gold"
)

score_label.pack(pady=5)

moves_label = tk.Label(
    right_frame,
    text="Moves: 0",
    font=("Arial", 14, "bold"),
    bg="#1a1a1a",
    fg="lightblue"
)

moves_label.pack(pady=5)

safe_label = tk.Label(
    right_frame,
    text="Safe Cells: 0",
    font=("Arial", 14),
    bg="#1a1a1a",
    fg="lightgreen"
)

safe_label.pack(pady=5)

danger_label = tk.Label(
    right_frame,
    text="Danger Cells: 0",
    font=("Arial", 14),
    bg="#1a1a1a",
    fg="red"
)

danger_label.pack(pady=5)

explored_label = tk.Label(
    right_frame,
    text="Explored Cells: 0",
    font=("Arial", 14),
    bg="#1a1a1a",
    fg="white"
)

explored_label.pack(pady=5)

logs_title = tk.Label(
    right_frame,
    text="AI THINKING LOGS",
    font=("Arial", 16, "bold"),
    bg="#1a1a1a",
    fg="orange"
)

logs_title.pack(pady=15)

# ================= LOG BOX ================= #

log_box = tk.Text(
    right_frame,
    width=40,
    height=18,
    bg="#0d0d0d",
    fg="lightgreen",
    font=("Consolas", 10),
    bd=2
)

log_box.pack(padx=10, pady=10)

log_box.config(state=tk.DISABLED)

# ================= HELPERS ================= #

def add_log(message):

    log_box.config(state=tk.NORMAL)

    log_box.insert(tk.END, message + "\n")

    log_box.see(tk.END)

    log_box.config(state=tk.DISABLED)

def restart_game():

    root.destroy()

    subprocess.Popen([sys.executable, "main.py"])

def get_adjacent_cells(x, y):

    adjacent = []

    if x > 0:
        adjacent.append((x - 1, y))

    if x < GRID_SIZE - 1:
        adjacent.append((x + 1, y))

    if y > 0:
        adjacent.append((x, y - 1))

    if y < GRID_SIZE - 1:
        adjacent.append((x, y + 1))

    return adjacent

# ================= PERCEPTS ================= #

def get_percepts():

    percepts = []

    adjacent = get_adjacent_cells(agent_x, agent_y)

    for x, y in adjacent:

        if world[x][y] == 'P':
            percepts.append("Breeze")

        if world[x][y] == 'W':
            percepts.append("Stench")

    if world[agent_x][agent_y] == 'G':
        percepts.append("Glitter")

    return percepts

# ================= AI LOGIC ================= #

# ================= AI LOGIC ================= #

def ai_move():

    global agent_x, agent_y
    global score, moves
    global recent_moves

    current = (agent_x, agent_y)

    visited.add(current)
    explored.add(current)

    percepts = get_percepts()

    add_log(f"[AI] Exploring ({agent_x}, {agent_y})")

    adjacent = get_adjacent_cells(agent_x, agent_y)

    # Reveal nearby objects
    for cell in adjacent:

        x, y = cell

        if world[x][y] != '':
            revealed_objects.add(cell)

    # SAFE AREA
    if "Breeze" not in percepts and "Stench" not in percepts:

        add_log("[AI] Area appears SAFE")

        for cell in adjacent:

            if cell not in dangerous_cells:
                safe_cells.add(cell)

    # PIT DETECTION
    if "Breeze" in percepts:

        add_log("[AI] Breeze detected -> PIT suspected nearby")

        for cell in adjacent:

            if cell not in visited:
                dangerous_cells.add(cell)

    # WUMPUS DETECTION
    if "Stench" in percepts:

        add_log("[AI] Stench detected -> WUMPUS suspected nearby")

        for cell in adjacent:

            if cell not in visited:
                dangerous_cells.add(cell)

    # ================= MOVE SELECTION ================= #

    possible_moves = []

    # PRIORITY 1 -> SAFE UNVISITED
    for cell in safe_cells:

        if cell not in visited:
            possible_moves.append(cell)

    # PRIORITY 2 -> NON DANGEROUS
    if not possible_moves:

        for cell in adjacent:

            if (
                cell not in dangerous_cells
                and recent_moves.count(cell) < 2
            ):
                possible_moves.append(cell)

    # PRIORITY 3 -> ANY ADJACENT
    if not possible_moves:
        possible_moves = adjacent

    # ================= SMART MOVE ================= #

    best_move = None

    # Prefer unexplored
    for move in possible_moves:

        if move not in explored:
            best_move = move
            break

    # Otherwise least repeated
    if best_move is None:

        filtered_moves = sorted(
            possible_moves,
            key=lambda x: recent_moves.count(x)
        )

        if filtered_moves:
            best_move = filtered_moves[0]

    # FINAL MOVE
    if best_move:

        agent_x, agent_y = best_move

        add_log(f"[AI] Moving to {best_move}")

        recent_moves.append(best_move)

        if len(recent_moves) > 10:
            recent_moves.pop(0)

    score -= 1
    moves += 1

    draw_world()

# ================= DRAW WORLD ================= #

# ================= DRAW WORLD ================= #

def draw_world():

    canvas.delete("all")

    for i in range(GRID_SIZE):

        for j in range(GRID_SIZE):

            x1 = j * CELL_SIZE
            y1 = i * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            cell = (i, j)

            # UNEXPLORED CELLS
            if cell not in explored and cell not in revealed_objects:

                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="#050505",
                    outline="#333333",
                    width=2
                )

                canvas.create_text(
                    x1 + CELL_SIZE // 2,
                    y1 + CELL_SIZE // 2,
                    text="?",
                    fill="gray",
                    font=("Arial", 28, "bold")
                )

            else:

                cell_color = "#1e1e1e"

                if cell in safe_cells:
                    cell_color = "#163616"

                if cell in dangerous_cells:
                    cell_color = "#3d1616"

                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=cell_color,
                    outline="white",
                    width=2
                )

                item = world[i][j]

                symbol = ""
                symbol_color = "white"

                if item == 'P':
                  symbol = "PIT"
                  symbol_color = "red"

                elif item == 'W':
                  symbol = "MONSTER"
                  symbol_color = "purple"

                elif item == 'G':
                   symbol = "GOLD"
                   symbol_color = "gold"

                if symbol:

                    # Highlight revealed objects
                    if cell in revealed_objects:

                        canvas.create_rectangle(
                            x1 + 5,
                            y1 + 5,
                            x2 - 5,
                            y2 - 5,
                            outline="yellow",
                            width=4
                        )

                    canvas.create_text(
                        x1 + CELL_SIZE // 2,
                        y1 + CELL_SIZE // 2,
                        text=symbol,
                        font=("Arial", 16, "bold"),
                        fill=symbol_color
                    )

    # DRAW AGENT
    canvas.create_oval(
        agent_y * CELL_SIZE + 25,
        agent_x * CELL_SIZE + 25,
        agent_y * CELL_SIZE + CELL_SIZE - 25,
        agent_x * CELL_SIZE + CELL_SIZE - 25,
        fill="deepskyblue",
        outline="white",
        width=4
    )

    canvas.create_text(
        agent_y * CELL_SIZE + CELL_SIZE // 2,
        agent_x * CELL_SIZE + CELL_SIZE // 2,
        text="AI",
        font=("Arial", 24)
    )

    # UPDATE DASHBOARD
    percepts = get_percepts()

    if percepts:

        status_label.config(
            text="Percepts: " + ", ".join(percepts),
            fg="red"
        )

    else:

        status_label.config(
            text="Percepts: SAFE",
            fg="lightgreen"
        )

    score_label.config(text=f"Score: {score}")

    moves_label.config(text=f"Moves: {moves}")

    safe_label.config(
        text=f"Safe Cells: {len(safe_cells)}"
    )

    danger_label.config(
        text=f"Danger Cells: {len(dangerous_cells)}"
    )

    explored_label.config(
        text=f"Explored Cells: {len(explored)}"
    )

    check_game_status()
# ================= GAME STATUS ================= #

# ================= GAME STATUS ================= #

def check_game_status():

    global score

    current = world[agent_x][agent_y]

    revealed_objects.add((agent_x, agent_y))

    # PIT
    if current == 'P':

        score -= 100

        add_log("[AI] Agent fell into PIT")

        messagebox.showerror(
            "GAME OVER",
            f"Agent fell into a PIT!\nFinal Score: {score}"
        )

        root.destroy()

    # WUMPUS
    elif current == 'W':

        score -= 100

        add_log("[AI] Wumpus killed the Agent")

        messagebox.showerror(
            "GAME OVER",
            f"Wumpus killed the Agent!\nFinal Score: {score}"
        )

        root.destroy()

    # GOLD
    elif current == 'G':

        score += 100

        add_log("[AI] GOLD FOUND SUCCESSFULLY")

        messagebox.showinfo(
            "VICTORY",
            f"Agent found the GOLD!\nFinal Score: {score}"
        )

        root.destroy()
# ================= BUTTONS ================= #

button_frame = tk.Frame(right_frame, bg="#1a1a1a")
button_frame.pack(pady=10)

restart_button = tk.Button(
    button_frame,
    text="Restart Simulation",
    font=("Arial", 12, "bold"),
    bg="darkred",
    fg="white",
    padx=15,
    pady=8,
    command=restart_game
)

restart_button.pack()

# ================= AI LOOP ================= #

def start_ai():

    ai_move()

    root.after(1200, start_ai)

# ================= START ================= #

add_log("[SYSTEM] AI Simulation Started")

draw_world()

root.after(1200, start_ai)

root.mainloop()