import tkinter as tk
import random

# ==================== ШАГ ПЕРВЫЙ: НАСТРОЙКА ====================
grid = 32  # Размер ячейки
cols = 10
rows = 20

root = tk.Tk()
root.title("Tetris — Canvas Edition")
root.resizable(False, False)
root.configure(bg='#1a1a2e')

# Главный контейнер
main_frame = tk.Frame(root, bg='#1a1a2e')
main_frame.pack(padx=20, pady=20)

# Игровое поле на Canvas
game_canvas = tk.Canvas(main_frame, width=cols*grid, height=rows*grid, 
                        bg='black', relief='sunken', bd=3, highlightthickness=0)
game_canvas.pack(side='left')

# Панель информации
info_frame = tk.Frame(main_frame, bg='#1a1a2e', width=150)
info_frame.pack(side='right', padx=20, fill='y')

score_label = tk.Label(info_frame, text="Score: 0", font=("Arial", 18, "bold"), 
                       bg='#1a1a2e', fg='white')
score_label.pack(pady=30)

tk.Label(info_frame, text="← → : Движение\n↑ : Поворот\n↓ : Ускорить", 
         font=("Arial", 11), bg='#1a1a2e', fg='#aaa', justify='left').pack(pady=20)

# ==================== ШАГ ВТОРОЙ: ИГРОВОЕ ПОЛЕ ====================
# В playfield хранятся ID фигур на canvas (или None)
playfield = []
for row in range(rows):
    playfield.append([None] * cols)

current_piece_items = []  # ID квадратов падающей фигуры на canvas

# ==================== ШАГ ТРЕТИЙ: ФИГУРЫ ====================
tetrominos = {
    'I': [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
    'J': [[1,0,0], [1,1,1], [0,0,0]],
    'L': [[0,0,1], [1,1,1], [0,0,0]],
    'O': [[1,1], [1,1]],
    'S': [[0,1,1],[1,1,0],[0,0,0]],
    'Z': [[1,1,0],[0,1,1],[0,0,0]],
    'T': [[0,1,0],[1,1,1],[0,0,0]]
}

# ==================== ШАГ ЧЕТВЁРТЫЙ: ЦВЕТА И ПЕРЕМЕННЫЕ ====================
colors = {
    'I': '#00ffff', 'O': '#ffff00', 'T': '#9933ff',
    'S': '#33cc33', 'Z': '#ff3333', 'J': '#3366ff', 'L': '#ff9933'
}

count = 0
score = 0
tetromino = None
tetromino_sequence = []
game_over = False

# ==================== ФУНКЦИЯ: РИСОВАНИЕ КВАДРАТА НА CANVAS ====================
def draw_square(canvas, col, row, color, outline='#222'):
    """Рисует квадрат в указанной ячейке сетки"""
    x1 = col * grid + 1
    y1 = row * grid + 1
    x2 = x1 + grid - 2
    y2 = y1 + grid - 2
    return canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline, width=1)

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
    global current_piece_items
    
    # Удаляем предыдущие квадраты падающей фигуры
    for item_id in current_piece_items:
        game_canvas.delete(item_id)
    current_piece_items = []
    
    if not tetromino or game_over:
        return
    
    color = colors[tetromino['name']]
    for row in range(len(tetromino['matrix'])):
        for col in range(len(tetromino['matrix'][0])):
            if tetromino['matrix'][row][col]:
                draw_row = tetromino['row'] + row
                draw_col = tetromino['col'] + col
                if draw_row >= 0:  # Рисуем только видимые части
                    item = draw_square(game_canvas, draw_col, draw_row, color)
                    current_piece_items.append(item)

# ==================== ШАГ ДЕВЯТЫЙ: ФИКСАЦИЯ И ОЧИСТКА ЛИНИЙ ====================
def place_tetromino():
    global score, tetromino, current_piece_items
    
    # Фиксируем фигуру в playfield (сохраняем ID квадратов)
    for row in range(len(tetromino['matrix'])):
        for col in range(len(tetromino['matrix'][0])):
            if tetromino['matrix'][row][col]:
                field_row = tetromino['row'] + row
                field_col = tetromino['col'] + col
                
                if field_row < 0:
                    return show_game_over()
                
                if 0 <= field_row < rows and 0 <= field_col < cols:
                    if playfield[field_row][field_col] is None:
                        item = draw_square(game_canvas, field_col, field_row, 
                                          colors[tetromino['name']])
                        playfield[field_row][field_col] = item
    
    # Очищаем список текущей фигуры
    for item_id in current_piece_items:
        game_canvas.delete(item_id)
    current_piece_items = []
    
    # Очистка заполненных строк
    row = rows - 1
    while row >= 0:
        if all(cell is not None for cell in playfield[row]):
            # Удаляем все квадраты в строке
            for col in range(cols):
                if playfield[row][col]:
                    game_canvas.delete(playfield[row][col])
                    playfield[row][col] = None
            
            # Сдвигаем все строки выше вниз
            for r in range(row, 0, -1):
                for c in range(cols):
                    if playfield[r-1][c]:
                        # Перемещаем квадрат на канвасе
                        game_canvas.move(playfield[r-1][c], 0, grid)
                        playfield[r][c] = playfield[r-1][c]
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
    
    # Затемнение поля
    overlay = game_canvas.create_rectangle(0, 0, cols*grid, rows*grid, 
                                           fill='black', stipple='gray12', width=0)
    
    game_canvas.create_text(cols*grid//2, rows*grid//2 - 20, 
                           text="GAME OVER!", font=("Arial", 24, "bold"),
                           fill='white')
    
    restart_btn = game_canvas.create_text(cols*grid//2, rows*grid//2 + 30,
                                         text="▶ Restart ◀", font=("Arial", 16),
                                         fill='#3366ff', cursor='hand2')
    
    def on_restart_click(event):
        game_canvas.delete(overlay)
        game_canvas.delete(restart_btn)
        restart_game()
    
    game_canvas.tag_bind(restart_btn, '<Button-1>', on_restart_click)

def restart_game():
    global score, game_over, tetromino, playfield, current_piece_items, count
    
    # Очистка canvas
    game_canvas.delete('all')
    
    # Сброс playfield
    playfield = []
    for row in range(rows):
        playfield.append([None] * cols)
        
    score = 0
    count = 0
    score_label.config(text="Score: 0")
    game_over = False
    current_piece_items = []
    tetromino = get_next_tetromino()
    game_loop()

# ==================== ШАГ ОДИНАДЦАТЫЙ: ОБРАБОТКА КЛАВИШ ====================
def on_key(event):
    global tetromino, count
    if game_over: 
        return
    
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
    if game_over: 
        return
    
    count += 1
    if count > 35:  # Скорость падения
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
