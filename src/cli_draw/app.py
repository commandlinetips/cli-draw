import curses
import pyperclip
from .config import load_config, get_colors, get_color_names, get_brushes

class Cell:
    def __init__(self, char, color_index):
        self.char = char
        self.color_index = color_index

class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.config = load_config()
        self.colors = get_colors(self.config)
        self.color_names = get_color_names(self.config)
        self.brushes = get_brushes(self.config)
        self.brush_char = self.brushes[0] if self.brushes else "#"
        self.color_index = 0
        self.drawing = False
        self.canvas_height = 10
        self.canvas_width = 80
        self.cells = []
        self.last_point = None
        self.message = ""
        self.undo_stack = []
        self.max_undo = 50
        self.set_brush_mode = False

    def sync_size(self):
        h, w = self.stdscr.getmaxyx()
        self.canvas_height = max(3, h - 3)
        self.canvas_width = max(10, w)
        if len(self.cells) != self.canvas_height:
            self.cells = [[Cell(" ", 0) for _ in range(self.canvas_width)] for _ in range(self.canvas_height)]
        for row in self.cells:
            while len(row) < self.canvas_width:
                row.append(Cell(" ", 0))
            while len(row) > self.canvas_width:
                row.pop()

    def setup(self):
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        for i, (_, _, curses_color) in enumerate(self.colors, start=1):
            curses.init_pair(i, curses_color, -1)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(0)
        print("\033[?1003h", end="", flush=True)
        self.stdscr.keypad(True)
        self.stdscr.nodelay(False)
        self.sync_size()

    def save_to_file(self):
        try:
            text = ""
            for row in self.cells:
                line = ""
                for cell in row:
                    ansi = self.colors[cell.color_index][1]
                    line += f"{ansi}{cell.char}\033[0m"
                text += line + "\n"
            with open("save.txt", "w") as f:
                f.write(text)
            self.message = "Saved to save.txt"
        except Exception as e:
            self.message = f"Error: {e}"
        self.render()

    def save_state(self):
        state = [[Cell(cell.char, cell.color_index) for cell in row] for row in self.cells]
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.cells = self.undo_stack.pop()
            self.message = "Undo"
        else:
            self.message = "Nothing to undo"

    def run(self):
        self.setup()
        try:
            while True:
                self.sync_size()
                self.render()
                key = self.stdscr.getch()
                if key in (ord("q"), 27):
                    return
                if key == 3:
                    return
                if key == ord("c"):
                    for row in self.cells:
                        for cell in row:
                            cell.char = " "
                            cell.color_index = 0
                    self.message = "Canvas cleared"
                    continue
                if key == ord("b"):
                    self.set_brush_mode = True
                    self.message = "Press key for new brush (ESC/q to cancel)"
                    continue
                if self.set_brush_mode:
                    if key in (ord("q"), 27):
                        self.set_brush_mode = False
                        self.message = ""
                    elif 32 <= key <= 126:
                        self.brush_char = chr(key)
                        self.set_brush_mode = False
                        self.message = f"Brush set to '{chr(key)}'"
                    continue
                if key in range(ord("0"), ord("8")):
                    self.color_index = 7 - (key - ord("0"))
                    self.message = f"Color {self.color_index}"
                    continue
                if key == ord("u"):
                    self.undo()
                    continue
                if key == ord("s"):
                    self.save_to_file()
                    continue
                if key == ord("y"):
                    self.message = "Copied to clipboard"
                    self.copy_to_clipboard()
                    continue
                if key == curses.KEY_MOUSE:
                    self.handle_mouse()
                    continue
                self.message = f"Key: {chr(key) if 32 <= key <= 126 else key}"
        finally:
            print("\033[?1003l", end="", flush=True)

    def paint(self, x, y):
        if not (0 <= x < self.canvas_width and 0 <= y < self.canvas_height):
            return
        if self.last_point is None:
            self.cells[y][x] = Cell(self.brush_char, self.color_index)
        else:
            last_x, last_y = self.last_point
            dx = abs(x - last_x)
            dy = -abs(y - last_y)
            sx = 1 if last_x < x else -1
            sy = 1 if last_y < y else -1
            err = dx + dy
            cx, cy = last_x, last_y
            while True:
                if 0 <= cx < self.canvas_width and 0 <= cy < self.canvas_height:
                    self.cells[cy][cx] = Cell(self.brush_char, self.color_index)
                if cx == x and cy == y:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    cx += sx
                if e2 <= dx:
                    err += dx
                    cy += sy
        self.last_point = (x, y)

    def handle_mouse(self):
        try:
            _, x, y, _, state = curses.getmouse()
        except curses.error:
            return
        if y >= self.canvas_height:
            return
        if state & (curses.BUTTON1_PRESSED | curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED):
            self.save_state()
            self.drawing = True
            self.paint(x, y)
        elif state & curses.BUTTON1_RELEASED:
            if self.drawing:
                self.paint(x, y)
            self.drawing = False
            self.last_point = None
        elif self.drawing and state & curses.REPORT_MOUSE_POSITION:
            self.paint(x, y)

    def render(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()
        for y in range(min(self.canvas_height, h - 3)):
            for x in range(min(self.canvas_width, w - 1)):
                try:
                    cell = self.cells[y][x]
                    self.stdscr.addstr(y, x, cell.char, curses.color_pair(cell.color_index + 1))
                except curses.error:
                    pass
        
        if self.set_brush_mode:
            status = "[ESC/q] Cancel  Press any key to set brush"
        else:
            status = f"[q] Quit  [c] Clear  [b] Set brush  [5-0] Color  [s] Save  [y] Copy  [u] Undo"
        
        if h > self.canvas_height + 1:
            remaining = w - len(status)
            offset = max(0, remaining // 2)
            try:
                self.stdscr.addstr(self.canvas_height + 1, offset, status[:w - offset - 1])
            except:
                pass
        if self.message and h > self.canvas_height + 2:
            try:
                self.stdscr.addstr(self.canvas_height + 2, 0, self.message[:w - 1])
                self.message = ""
            except:
                pass
        self.stdscr.refresh()

def run():
    curses.wrapper(lambda stdscr: App(stdscr).run())

def main():
    run()
