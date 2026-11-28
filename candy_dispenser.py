"""
PEZ Candy Dispenser - ARRAY-BASED STACK (DAA Assignment 01)

The file has 4 parts, in the order you would explain them:
  PART 1  ArrayStack   - the algorithm (push, pop, top, len, is_empty)
  PART 2  Candy        - what a candy is (colour + shape, unique per slot)
  PART 3  Drawing      - candy shapes and the SPRING rule
  PART 4  App          - Tkinter window, buttons and error handling

Run:  python3 candy_dispenser.py
"""
import tkinter as tk

# ----------------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------------
CAPACITY = 8            # how many candies the dispenser holds
STEP = 40               # pixels the spring moves on EVERY push / pop
CANDY_W = 120
CANDY_H = STEP - 4      # 4 px gap between candies

# Canvas geometry (remember: y grows DOWNWARDS on a canvas)
CX = 160                                   # centre line of the tube
TUBE_L, TUBE_R = CX - 80, CX + 80
BASE_Y = 520                               # fixed bottom the spring is attached to
SPRING_MIN = 40                            # spring height when fully compressed
TOP_Y = BASE_Y - (CAPACITY * STEP + SPRING_MIN)   # the exit: top candy is ALWAYS here
PLATE_H = 8


# ======================================================================
# PART 1 - THE ALGORITHM: ARRAY-BASED STACK
# ======================================================================
class DispenserFull(Exception):
    pass


class DispenserEmpty(Exception):
    pass


class ArrayStack:
    """Fixed-size list + an integer `_size`.

    _size is BOTH the number of items AND the index of the next free slot,
    so every operation is just one index lookup -> O(1).
    """

    def __init__(self, capacity):
        self._data = [None] * capacity     # pre-allocated array, all slots empty
        self._size = 0

    def push(self, item):                  # O(1)
        if self._size == len(self._data):
            raise DispenserFull("The dispenser is full")
        self._data[self._size] = item      # put it in the next free slot
        self._size += 1

    def pop(self):                         # O(1)
        if self.is_empty():
            raise DispenserEmpty("The dispenser is empty")
        self._size -= 1
        item = self._data[self._size]
        self._data[self._size] = None      # free the slot
        return item

    def top(self):                         # O(1)  (look, don't remove)
        if self.is_empty():
            raise DispenserEmpty("The dispenser is empty")
        return self._data[self._size - 1]

    def __len__(self):                     # O(1)  -> makes len(stack) work
        return self._size

    def is_empty(self):                    # O(1)
        return self._size == 0

    def slots(self):                       # copy of the array, only used for display
        return list(self._data)


# ======================================================================
# PART 2 - THE CANDY
# ======================================================================
# One look per SLOT (flavour, colour, shape). Because slot numbers are
# unique, no two candies inside the dispenser can ever share a colour or
# a shape - guaranteed by construction, no checking needed.
LOOKS = [
    ("Cherry",    "#e63946", "circle"),
    ("Orange",    "#f77f00", "rectangle"),
    ("Lemon",     "#fcdc2a", "diamond"),
    ("Lime",      "#38b000", "triangle"),
    ("Ice",       "#00bbf9", "hexagon"),
    ("Grape",     "#b388eb", "trapezoid"),
    ("Bubblegum", "#ff70a6", "parallelogram"),
    ("Caramel",   "#c68642", "cross"),
]


class Candy:
    def __init__(self, number, slot):
        self.number = number                                  # 1st, 2nd, 3rd ... candy made
        self.flavour, self.color, self.shape = LOOKS[slot]

    def __str__(self):
        return f"#{self.number} {self.flavour} ({self.shape})"


# ======================================================================
# PART 3 - DRAWING: CANDY SHAPES
# ======================================================================
# Each polygon is a list of (x, y) points as FRACTIONS of the candy's box
# (0,0 = top-left corner, 1,1 = bottom-right corner), so one loop can
# scale any shape to any size.
POLYGONS = {
    "diamond":       [(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)],
    "triangle":      [(0.5, 0), (1, 1), (0, 1)],
    "hexagon":       [(0.2, 0), (0.8, 0), (1, 0.5), (0.8, 1), (0.2, 1), (0, 0.5)],
    "trapezoid":     [(0.2, 0), (0.8, 0), (1, 1), (0, 1)],
    "parallelogram": [(0.2, 0), (1, 0), (0.8, 1), (0, 1)],
    "cross":         [(0.35, 0), (0.65, 0), (0.65, 0.3), (1, 0.3), (1, 0.7), (0.65, 0.7),
                      (0.65, 1), (0.35, 1), (0.35, 0.7), (0, 0.7), (0, 0.3), (0.35, 0.3)],
}


def draw_candy(canvas, candy, x1, y1, x2, y2):
    """Draw one candy inside the box (x1,y1)-(x2,y2) using canvas shapes."""
    style = dict(fill=candy.color, outline="black", width=2)
    if candy.shape == "circle":
        canvas.create_oval(x1, y1, x2, y2, **style)
    elif candy.shape == "rectangle":
        canvas.create_rectangle(x1, y1, x2, y2, **style)
    else:                                              # everything else is a polygon
        w, h = x2 - x1, y2 - y1
        points = []
        for fx, fy in POLYGONS[candy.shape]:
            points += [x1 + fx * w, y1 + fy * h]       # scale fractions to pixels
        canvas.create_polygon(points, **style)


# ======================================================================
# PART 4 - THE APP (window, buttons, error handling, SPRING)
# ======================================================================
class App:
    def __init__(self, root):
        root.title("PEZ Candy Dispenser - Array-Based Stack")
        self.stack = ArrayStack(CAPACITY)
        self.next_number = 1

        # --- left: the dispenser drawing ---
        self.canvas = tk.Canvas(root, width=320, height=580, bg="#0b132b", highlightthickness=0)
        self.canvas.pack(side="left", padx=10, pady=10)

        # --- right: buttons, array view, message log ---
        panel = tk.Frame(root)
        panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        row = tk.Frame(panel)
        row.pack(fill="x")
        buttons = [("Push", self.do_push), ("Pop", self.do_pop), ("Top", self.do_top),
                   ("Len", self.do_len), ("Is Empty", self.do_is_empty)]
        for text, action in buttons:
            # every button goes through safely(), so NOTHING can crash the program
            tk.Button(row, text=text, width=9,
                      command=lambda a=action: self.safely(a)).pack(side="left", padx=3)

        self.array_label = tk.Label(panel, font=("Courier", 10), anchor="w",
                                    justify="left", wraplength=480)
        self.array_label.pack(fill="x", pady=8)

        self.log = tk.Text(panel, width=58, height=24, font=("Courier", 10))
        self.log.pack(fill="both", expand=True)
        self.log.tag_configure("ok", foreground="#15803d")
        self.log.tag_configure("info", foreground="#1d4ed8")
        self.log.tag_configure("error", foreground="#dc2626")

        self.draw()
        self.show("READY", [f"Empty dispenser, capacity {CAPACITY}."], "info")

    # ---------------- error handling (one place for all buttons) ----------------
    def safely(self, action):
        try:
            action()
        except (DispenserFull, DispenserEmpty) as err:     # the two expected errors
            self.show("ERROR", [str(err)], "error")
        except Exception as err:                           # safety net: never crash
            self.show("UNEXPECTED ERROR", [str(err)], "error")

    def show(self, title, lines, tag):
        self.log.insert("end", f"== {title} ==\n", tag)
        for line in lines:
            self.log.insert("end", f"   {line}\n")
        self.log.insert("end", "\n")
        self.log.see("end")

    # ---------------- the five buttons ----------------
    def do_push(self):
        # "% CAPACITY" only avoids an index error when the dispenser is full;
        # push() then raises DispenserFull before the candy is ever used.
        candy = Candy(self.next_number, len(self.stack) % CAPACITY)
        self.stack.push(candy)
        self.next_number += 1                     # only counts candies that really got in
        self.draw()
        self.show("PUSH", [f"Added {candy}",
                           f"Stored in _data[{len(self.stack) - 1}]",
                           f"Slots left: {CAPACITY - len(self.stack)}"], "ok")

    def do_pop(self):
        candy = self.stack.pop()
        self.draw()
        new_top = "none - dispenser is now empty" if self.stack.is_empty() else self.stack.top()
        self.show("POP", [f"Removed {candy}",
                          f"New top: {new_top}",
                          f"Slots left: {CAPACITY - len(self.stack)}"], "ok")

    def do_top(self):
        candy = self.stack.top()
        below = len(self.stack) - 1
        self.show("TOP", [f"Top candy: {candy}",
                          f"Colour {candy.color}, shape {candy.shape}",
                          f"At index {below}, with {below} candies beneath it"], "info")

    def do_len(self):
        n = len(self.stack)
        self.show("LEN", [f"Candies inside: {n} of {CAPACITY}",
                          f"Fill level: {100 * n // CAPACITY}%"], "info")

    def do_is_empty(self):
        if self.stack.is_empty():
            self.show("IS EMPTY", ["True - nothing to dispense, push some candy!"], "info")
        else:
            self.show("IS EMPTY", [f"False - {len(self.stack)} candies are waiting."], "info")

    # ---------------- drawing everything from the stack state ----------------
    def draw(self):
        c = self.canvas
        c.delete("all")                      # wipe and redraw: picture can never drift from data
        size = len(self.stack)

        # >>> THE SPRING RULE <<<
        # The plate sits on the spring. Each push moves it DOWN by STEP,
        # each pop moves it UP by STEP (y grows downward).
        plate_y = TOP_Y + size * STEP

        # tube, base and head
        c.create_rectangle(TUBE_L, TOP_Y, TUBE_R, BASE_Y, outline="#38bdf8", width=3)
        c.create_rectangle(TUBE_L - 10, BASE_Y, TUBE_R + 10, BASE_Y + 15, fill="#475569")
        c.create_rectangle(TUBE_L - 10, TOP_Y - 35, TUBE_R + 10, TOP_Y - 5, fill="#d97706")
        c.create_text(CX, TOP_Y - 20, text="PEZ", font=("Helvetica", 12, "bold"))
        c.create_text(TUBE_R + 8, TOP_Y + STEP / 2, text="<- EXIT", anchor="w",
                      fill="#facc15", font=("Helvetica", 9, "bold"))

        # spring: a zigzag line from the fixed base up to the plate
        spring_top = plate_y + PLATE_H
        points = [CX, BASE_Y]
        coils = 14
        for k in range(1, coils):
            y = BASE_Y - (BASE_Y - spring_top) * k / coils
            points += [CX + (25 if k % 2 else -25), y]
        points += [CX, spring_top]
        c.create_line(points, fill="#cbd5e1", width=3)
        c.create_rectangle(TUBE_L + 4, plate_y, TUBE_R - 4, spring_top, fill="#94a3b8")

        # candies, stacked upward from the plate (index 0 sits on the plate)
        for i in range(size):
            candy = self.stack.slots()[i]
            y2 = plate_y - i * STEP - 2
            y1 = y2 - CANDY_H
            draw_candy(c, candy, CX - CANDY_W / 2, y1, CX + CANDY_W / 2, y2)
            c.create_text(CX, (y1 + y2) / 2, text=f"[{i}] {candy.flavour}",
                          font=("Helvetica", 9, "bold"))

        # live view of the underlying array
        cells = [f"#{x.number}" if x else "None" for x in self.stack.slots()]
        self.array_label.config(text=f"_data = [{', '.join(cells)}]\n_size = {size}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()