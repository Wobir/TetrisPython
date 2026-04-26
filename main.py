import tkinter as tk
import random

# ==================== ШАГ ПЕРВЫЙ: НАСТРОЙКА ====================
grid = 32  # Размер ячейки
cols = 10
rows = 20

root = tk.Tk()
root.title("Tetris — Widget Zoo Edition")
root.resizable(False, False)
root.configure(bg='#1a1a2e')

# Главный контейнер
main_frame = tk.Frame(root, bg='#1a1a2e')
main_frame.pack(padx=20, pady=20)

# Игровое поле
game_frame = tk.Frame(main_frame, width=cols*grid, height=rows*grid, bg='black', relief='sunken', bd=3)
game_frame.pack(side='left')
game_frame.pack_propagate(False)

# Панель информации
info_frame = tk.Frame(main_frame, bg='#1a1a2e', width=150)
info_frame.pack(side='right', padx=20, fill='y')

score_label = tk.Label(info_frame, text="Score: 0", font=("Arial", 18, "bold"), bg='#1a1a2e', fg='white')
score_label.pack(pady=30)

tk.Label(info_frame, text="← → : Движение\n↑ : Поворот\n↓ : Ускорить", 
         font=("Arial", 11), bg='#1a1a2e', fg='#aaa', justify='left').pack(pady=20)

# ==================== ШАГ ВТОРОЙ: ИГРОВОЕ ПОЛЕ ====================
# В playfield хранятся ссылки на реальные виджеты
playfield = []
for row in range(-2, rows):
    playfield.append([None] * cols)

current_piece_widgets = []  # Виджеты падающей фигуры

# ==================== ШАГ ТРЕТИЙ: ФИГУРЫ ====================
tetrominos = {
    'I': [[0,0,0,0],
          [1,1,1,1],
          [0,0,0,0],
          [0,0,0,0]],
    'J': [[1,0,0],
          [1,1,1],
          [0,0,0]],
    'L': [[0,0,1],
          [1,1,1],
          [0,0,0]],
    'O': [[1,1],
          [1,1]],
    'S': [[0,1,1],[1,1,0],[0,0,0]],
    'Z': [[1,1,0],[0,1,1],[0,0,0]],
    'T': [[0,1,0],[1,1,1],[0,0,0]]
}

# ==================== ШАГ ЧЕТВЁРТЫЙ: ЦВЕТА И ПЕРЕМЕННЫЕ ====================
colors = {
    'I': 'cyan', 'O': 'yellow', 'T': 'purple',
    'S': 'green', 'Z': 'red', 'J': 'blue', 'L': 'orange'
}

count = 0
score = 0
tetromino = None
tetromino_sequence = []
game_over = False

# ==================== ВИДЖЕТ-ФУНКЦИЯ: РАЗНООБРАЗНЫЕ БЛОКИ ====================
def create_block_widget(parent, shape_name):
    """Возвращает разный виджет в зависимости от типа фигуры"""
    size = 30
    
    if shape_name == 'I':
        w = tk.Button(parent, text='I', bg='#00ffff', fg='#000', font=('Arial', 10, 'bold'), 
                      relief='raised', bd=2, command=None)
    elif shape_name == 'O':
        w = tk.Label(parent, text='●', bg='#ffff00', fg='#333', font=('Arial', 14), 
                     relief='sunken', bd=1)
    elif shape_name == 'T':
        w = tk.Checkbutton(parent, bg='#9933ff', activebackground='#9933ff', 
                           indicatoron=0, bd=2, relief='raised', command=None)
    elif shape_name == 'S':
        w = tk.Radiobutton(parent, bg='#33cc33', activebackground='#33cc33', 
                           indicatoron=0, bd=2, relief='raised', command=None)
    elif shape_name == 'Z':
        w = tk.Spinbox(parent, bg='#ff3333', fg='white', from_=0, to=9, width=2, 
                       state='readonly', font=('Arial', 8), bd=1)
    elif shape_name == 'J':
        w = tk.Entry(parent, bg='#3366ff', fg='white', justify='center', 
                     state='readonly', font=('Arial', 8), bd=2, relief='sunken')
        w.insert(0, 'J')
    elif shape_name == 'L':
        w = tk.Scale(parent, bg='#ff9933', from_=0, to=10, orient='horizontal', 
                     length=28, showvalue=0, sliderlength=16, highlightthickness=0, bd=0)
    else:
        w = tk.Label(parent, bg='gray')
        
    # place() принудительно задаёт размер, чтобы все блоки вписывались в сетку
    w.place(width=size, height=size)
    return w

# ==================== ШАГ ПЯТЫЙ: ГЕНЕРАЦИЯ ПОСЛЕДОВАТЕЛЬНОСТИ ====================
def get_random_int(min_val, max_val):
    return random.randint(min_val, max_val)

def generate_sequence():
    global tetromino_sequence
    sequence = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    while sequence:
        rand = get_random_int(0, len(sequence) - 1)
        name = sequence.pop(rand)
        tetromino_sequence.append(name)

# ==================== ШАГ ШЕСТОЙ: ПОЛУЧЕНИЕ СЛЕДУЮЩЕЙ ФИГУРЫ ====================
def get_next_tetromino():
    global tetromino_sequence
    if not tetromino_sequence:
        generate_sequence()
    
    name = tetromino_sequence.pop()
    matrix = tetrominos[name]
    col = cols // 2 - len(matrix[0]) // 2
    row = -1 if name == 'I' else -2
    return {'name': name, 'matrix': matrix, 'row': row, 'col': col}

# ==================== ШАГ СЕДЬМОЙ: ПОВОРОТ МАТРИЦЫ ====================
def rotate(matrix):
    N = len(matrix) - 1
    result = []
    for i in range(len(matrix[0])):
        new_row = []
        for j in range(len(matrix)):
            new_row.append(matrix[N - j][i])
        result.append(new_row)
    return result

# ==================== ШАГ ВОСЬМОЙ: ПРОВЕРКА КОЛЛИЗИЙ ====================
def is_valid_move(matrix, cell_row, cell_col):
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if matrix[row][col]:
                new_col = cell_col + col
                new_row = cell_row + row
                if new_col < 0 or new_col >= cols or new_row >= rows:
                    return False
                if new_row >= 0 and playfield[new_row][new_col] is not None:
                    return False
    return True

# ==================== ОТРИСОВКА ТЕКУЩЕЙ ФИГУРЫ ====================
def draw_current_piece():
    global current_piece_widgets
    for widget in current_piece_widgets:
        widget.place_forget()
        widget.destroy()
    current_piece_widgets = []
    
    if not tetromino or game_over:
        return
    
    for row in range(len(tetromino['matrix'])):
        for col in range(len(tetromino['matrix'][0])):
            if tetromino['matrix'][row][col]:
                draw_row = tetromino['row'] + row
                draw_col = tetromino['col'] + col
                if draw_row >= 0:
                    widget = create_block_widget(game_frame, tetromino['name'])
                    widget.place(x=draw_col * grid + 1, y=draw_row * grid + 1)
                    current_piece_widgets.append(widget)

# ==================== ШАГ ДЕВЯТЫЙ: ФИКСАЦИЯ И ОЧИСТКА ЛИНИЙ ====================
def place_tetromino():
    global score, tetromino, current_piece_widgets
    
    # Переносим виджеты в playfield
    for row in range(len(tetromino['matrix'])):
        for col in range(len(tetromino['matrix'][0])):
            if tetromino['matrix'][row][col]:
                field_row = tetromino['row'] + row
                field_col = tetromino['col'] + col
                
                if field_row < 0:
                    return show_game_over()
                
                if playfield[field_row][field_col] is None:
                    widget = create_block_widget(game_frame, tetromino['name'])
                    widget.place(x=field_col * grid + 1, y=field_row * grid + 1)
                    playfield[field_row][field_col] = widget
    
    for widget in current_piece_widgets:
        widget.destroy()
    current_piece_widgets = []
    
    # Очистка заполненных строк
    row = rows - 1
    while row >= 0:
        if all(cell is not None for cell in playfield[row]):
            for col in range(cols):
                if playfield[row][col]:
                    playfield[row][col].destroy()
                    playfield[row][col] = None
            
            for r in range(row, 0, -1):
                for c in range(cols):
                    if playfield[r-1][c]:
                        widget = playfield[r-1][c]
                        widget.place_configure(y=r * grid + 1)
                        playfield[r][c] = widget
                        playfield[r-1][c] = None
                    else:
                        playfield[r][c] = None
            playfield[0] = [None] * cols
            
            score += 100
            score_label.config(text=f"Score: {score}")
        else:
            row -= 1
    
    tetromino = get_next_tetromino()
    draw_current_piece()

# ==================== ШАГ ДЕСЯТЫЙ: КОНЕЦ ИГРЫ ====================
def show_game_over():
    global game_over
    game_over = True
    
    overlay = tk.Frame(game_frame, bg='black')
    overlay.place(relwidth=1, relheight=1)
    
    tk.Label(overlay, text="GAME OVER!", font=("Arial", 24, "bold"),
             bg='black', fg='white').place(relx=0.5, rely=0.45, anchor='center')
    
    tk.Button(overlay, text="Restart", font=("Arial", 14), command=restart_game,
              bg='#3366ff', fg='white', activebackground='#5588ff', 
              cursor='hand2', bd=0).place(relx=0.5, rely=0.65, anchor='center')

def restart_game():
    global score, game_over, tetromino, playfield, current_piece_widgets, count
    
    for widget in game_frame.winfo_children():
        widget.destroy()
        
    playfield = []
    for row in range(-2, rows):
        playfield.append([None] * cols)
        
    score = 0
    count = 0
    score_label.config(text="Score: 0")
    game_over = False
    current_piece_widgets = []
    tetromino = get_next_tetromino()
    game_loop()

# ==================== ШАГ ОДИНАДЦАТЫЙ: ОБРАБОТКА КЛАВИШ ====================
def on_key(event):
    global tetromino, count
    if game_over: return
    
    key = event.keysym
    if key in ('Left', 'Right'):
        direction = -1 if key == 'Left' else 1
        new_col = tetromino['col'] + direction
        if is_valid_move(tetromino['matrix'], tetromino['row'], new_col):
            tetromino['col'] = new_col
            draw_current_piece()
            
    elif key == 'Up':
        rotated = rotate(tetromino['matrix'])
        if is_valid_move(rotated, tetromino['row'], tetromino['col']):
            tetromino['matrix'] = rotated
            draw_current_piece()
            
    elif key == 'Down':
        new_row = tetromino['row'] + 1
        if not is_valid_move(tetromino['matrix'], new_row, tetromino['col']):
            tetromino['row'] = new_row - 1
            place_tetromino()
        else:
            tetromino['row'] = new_row
        draw_current_piece()

root.bind_all('<Key>', on_key)

# ==================== ШАГ ДВЕНАДЦАТЫЙ: ГЛАВНЫЙ ЦИКЛ ====================
def game_loop():
    global count, tetromino
    if game_over: return
    
    count += 1
    if count > 35:
        count = 0
        new_row = tetromino['row'] + 1
        if not is_valid_move(tetromino['matrix'], new_row, tetromino['col']):
            tetromino['row'] = new_row - 1
            place_tetromino()
        else:
            tetromino['row'] = new_row
            draw_current_piece()
            
    root.after(100, game_loop)

# ==================== ЗАПУСК ====================
def start_game():
    global tetromino, game_over, score, count
    tetromino = get_next_tetromino()
    game_over = False
    score = 0
    count = 0
    score_label.config(text="Score: 0")
    game_loop()

start_game()
root.mainloop()
