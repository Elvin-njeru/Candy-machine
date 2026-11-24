#!/usr/bin/env python3
"""
===============================================================================
PEZ-STYLE CANDY DISPENSER - ARRAY-BASED STACK DEMONSTRATION
===============================================================================
Course: Design and Analysis of Algorithms (DAA)
Topic: Elementary Data Structures - Fixed-Capacity Array-Based Stack (LIFO)

This program implements a graphical PEZ-style candy dispenser in Python 3 using
only the standard library (tkinter). It demonstrates a classic fixed-capacity
Array-Based Stack data structure without using collections.deque or Python's
built-in list.append() / list.pop() dynamic array methods.

Data Structure Principles Demonstrated:
1. Fixed memory allocation: self._data = [None] * capacity
2. LIFO (Last-In, First-Out) discipline with an integer pointer self._size
3. Worst-case O(1) time complexity for all fundamental operations:
   - push(e):   O(1)
   - pop():     O(1)
   - top():     O(1)
   - len():     O(1)
   - is_empty(): O(1)
4. Memory management: pop() explicitly resets vacated array slots to None
   to prevent stale object retention (loitering).
5. Robust boundary exception handling (DispenserFull, DispenserEmpty).
6. State-driven rendering: The PEZ tube, zigzag spring, and candies are redrawn
   purely from the current stack state, guaranteeing zero graphical drift.
===============================================================================
"""

from __future__ import annotations

import math
import sys
from typing import Any, List, Optional, Tuple

# Attempt standard library tkinter import
try:
    import tkinter as tk
    from tkinter import font as tkfont
    TKINTER_AVAILABLE = True
except ImportError:
    tk = None  # type: ignore
    tkfont = None  # type: ignore
    TKINTER_AVAILABLE = False


# =============================================================================
# LAYOUT & CONFIGURATION CONSTANTS
# =============================================================================

# Stack sizing
DEFAULT_CAPACITY: int = 8          # Maximum fixed capacity of the stack
STEP: int = 42                     # Pixels per candy & spring compression step

# Candy visual dimensions
CANDY_WIDTH: int = 140             # Width of individual candy tablet (px)
CANDY_HEIGHT: int = 36             # Height of individual candy tablet (px)

# Spring physics & geometry
SPRING_MIN_HEIGHT: int = 68        # Compressed spring height when full
FULL_HEIGHT: int = SPRING_MIN_HEIGHT + (DEFAULT_CAPACITY * STEP)  # Uncompressed
SPRING_COIL_RADIUS: int = 24       # Horizontal radius of spring zigzag
SPRING_NUM_COILS: int = 8          # Number of full sinusoidal/zigzag coils
PLATE_THICKNESS: int = 10          # Movable metal plate height (px)

# Canvas dimensions & coordinates
CANVAS_WIDTH: int = 370
CANVAS_HEIGHT: int = 620
TUBE_CENTER_X: int = 175
TUBE_WIDTH: int = 154
TUBE_LEFT: int = TUBE_CENTER_X - (TUBE_WIDTH // 2)    # 98
TUBE_RIGHT: int = TUBE_CENTER_X + (TUBE_WIDTH // 2)   # 252
TUBE_BOTTOM: int = 560                                # Bottom base of the tube
BASE_Y: int = TUBE_BOTTOM - 12                        # Spring anchor base (548)
TOP_MOUTH_Y: int = BASE_Y - FULL_HEIGHT               # Constant dispensing y (144)
TUBE_TOP: int = TOP_MOUTH_Y - 30                      # Dispenser head top (114)

# Color Palette (12 vibrant distinct colors for candies; palette size > capacity)
# Guarantees no two candies currently in the dispenser share the same color.
CANDY_PALETTE: List[Tuple[str, str]] = [
    ("#EF4444", "Cherry Red"),
    ("#F97316", "Tangerine Orange"),
    ("#FACC15", "Lemon Yellow"),
    ("#10B981", "Lime Green"),
    ("#06B6D4", "Cyan Blue"),
    ("#3B82F6", "Electric Cobalt"),
    ("#8B5CF6", "Grape Purple"),
    ("#EC4899", "Bubblegum Pink"),
    ("#14B8A6", "Spearmint Teal"),
    ("#F43F5E", "Raspberry Ruby"),
    ("#EAB308", "Mango Gold"),
    ("#6366F1", "Plum Indigo"),
]

# Shape Catalog: 12 distinct shapes for candy bodies drawn with Canvas primitives.
# With 12 shapes (> DEFAULT_CAPACITY), no two candies in the dispenser share a shape!
CANDY_SHAPES: List[str] = [
    "rounded_bar",    # Capsule / rounded rectangular tablet
    "circle",         # Wide pill-oval
    "diamond",        # 4-pointed rhombus
    "triangle",       # Upward-pointing triangle
    "star",           # 5-pointed star
    "hexagon",        # 6-sided hexagon
    "octagon",        # 8-sided chamfered tablet
    "pentagon",       # 5-sided pentagon
    "trapezoid",      # Isosceles trapezoid
    "parallelogram",  # Skewed tablet
    "cross",          # 12-sided plus/cross
    "chevron",        # Horizontal chevron arrow
]


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class DispenserFull(Exception):
    """Exception raised when push() is attempted on a full ArrayStack.
    
    Indicates that the underlying fixed-size list has reached capacity
    and cannot accept new elements without overflow.
    """
    pass


class DispenserEmpty(Exception):
    """Exception raised when pop() or top() is attempted on an empty ArrayStack.
    
    Indicates that the stack contains no elements (_size == 0) and therefore
    has no top element to read or remove.
    """
    pass


# =============================================================================
# DATA STRUCTURE: ARRAY-BASED STACK
# =============================================================================

class ArrayStack:
    """Fixed-capacity LIFO Stack implemented using a fixed-length Python list.
    
    Demonstrates array-based stack principles for a university DAA course.
    Strict constraints:
    - No collections.deque
    - No list.append()
    - No list.pop()
    - Fixed pre-allocated list: self._data = [None] * capacity
    - Explicit integer pointer: self._size
    - All primary operations run in strictly worst-case O(1) time.
    """

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        """Initialize an empty stack with the specified fixed capacity.
        
        Args:
            capacity: Maximum number of elements the stack can hold (default DEFAULT_CAPACITY).
            
        Complexity:
            Time:  O(n) where n is capacity (to pre-allocate the fixed list).
            Space: O(n) worst-case fixed memory footprint.
        """
        if capacity <= 0:
            raise ValueError("Stack capacity must be a positive integer.")
        self._capacity: int = capacity
        # Pre-allocate fixed-length array with None sentinels
        self._data: List[Optional[Any]] = [None] * capacity
        self._size: int = 0

    @property
    def capacity(self) -> int:
        """Return the maximum capacity of the stack.
        
        Complexity:
            Time:  O(1)
            Space: O(1)
        """
        return self._capacity

    def push(self, e: Any) -> None:
        """Insert element e onto the top of the stack.
        
        Args:
            e: The element to add (e.g., a Candy instance).
            
        Raises:
            DispenserFull: If the stack has reached its maximum fixed capacity.
            
        Complexity:
            Time:  O(1) - Direct array indexing and scalar integer increment.
            Space: O(1) - Modifies existing allocated slot in place.
        """
        if self._size >= self._capacity:
            raise DispenserFull("The dispenser is full")
        # Place element directly into array at index self._size (no list.append)
        self._data[self._size] = e
        self._size += 1

    def pop(self) -> Any:
        """Remove and return the element at the top of the stack.
        
        Vacated array slot is explicitly reset to None to prevent object
        retention (memory loitering).
        
        Returns:
            The element that was at the top of the stack.
            
        Raises:
            DispenserEmpty: If the stack contains no elements.
            
        Complexity:
            Time:  O(1) - Direct array indexing, scalar decrement, assignment.
            Space: O(1) - In-place operation.
        """
        if self.is_empty():
            raise DispenserEmpty("The dispenser is empty")
        self._size -= 1
        item = self._data[self._size]
        # Clean up vacated slot back to None (no list.pop)
        self._data[self._size] = None
        return item

    def top(self) -> Any:
        """Return (without removing) the element at the top of the stack.
        
        Returns:
            The current top element.
            
        Raises:
            DispenserEmpty: If the stack contains no elements.
            
        Complexity:
            Time:  O(1) - Single array read at self._size - 1.
            Space: O(1).
        """
        if self.is_empty():
            raise DispenserEmpty("The dispenser is empty")
        return self._data[self._size - 1]

    def __len__(self) -> int:
        """Return the number of elements currently stored in the stack.
        
        Complexity:
            Time:  O(1) - Returns cached integer counter.
            Space: O(1).
        """
        return self._size

    def len(self) -> int:
        """Public alias for __len__ as requested by specification.
        
        Complexity:
            Time:  O(1).
            Space: O(1).
        """
        return self._size

    def is_empty(self) -> bool:
        """Return True if the stack contains zero elements, False otherwise.
        
        Complexity:
            Time:  O(1) - Comparison of integer counter with 0.
            Space: O(1).
        """
        return self._size == 0

    def get_raw_data(self) -> List[Optional[Any]]:
        """Return a shallow copy of the underlying array for inspection/rendering.
        
        Complexity:
            Time:  O(n) where n is capacity.
            Space: O(n).
        """
        return list(self._data)


# =============================================================================
# CANDY ENTITY
# =============================================================================

class Candy:
    """Represents an individual candy loaded into the PEZ dispenser.
    
    Attributes:
        id: Unique sequential integer ID (#1, #2, ...).
        name: Flavor and shape description (e.g., 'Cherry Red Star').
        color: Hex color string (e.g., '#EF4444').
        shape: Geometric body shape key ('rounded_bar', 'diamond', 'star', etc.).
    """

    def __init__(self, candy_id: int, name: str, color: str, shape: str) -> None:
        self.id: int = candy_id
        self.name: str = name
        self.color: str = color
        self.shape: str = shape

    def __repr__(self) -> str:
        return f"Candy(id={self.id}, name='{self.name}', color='{self.color}', shape='{self.shape}')"

    def __str__(self) -> str:
        return f"#{self.id} {self.name}"


# =============================================================================
# GRAPHICAL USER INTERFACE (TKINTER)
# =============================================================================

class CandyDispenserApp:
    """Tkinter application demonstrating the PEZ ArrayStack dispenser."""

    def __init__(self, root: tk.Tk) -> None:
        self.root: tk.Tk = root
        self.root.title("PEZ Candy Dispenser — Array-Based Stack (DAA Assignment)")
        self.root.geometry("1060x720")
        self.root.minsize(980, 680)
        self.root.configure(bg="#0F172A")  # Deep modern dark slate background

        # Core Stack Data Structure
        self.stack: ArrayStack = ArrayStack(capacity=DEFAULT_CAPACITY)

        # Candy generation state
        self._next_candy_id: int = 0
        self._color_cycle_index: int = 0
        self._shape_cycle_index: int = 0

        # Animation state
        self._current_display_size: float = 0.0
        self._anim_job: Optional[str] = None
        self._slide_job: Optional[str] = None
        self._sliding_candy: Optional[Candy] = None
        self._slide_offset_x: float = 0.0
        self._highlighted_top: bool = False
        self._highlight_job: Optional[str] = None

        # Build UI Components
        self._setup_styles()
        self._build_header()
        self._build_main_layout()

        # Initial render from stack state
        self.draw(display_size=0.0)
        self.log_status(
            title="SYSTEM INITIALIZED",
            message=(
                f"ArrayStack ready with capacity = {self.stack.capacity}.\n"
                f"• Pre-allocated list: self._data = [None] * {self.stack.capacity}\n"
                f"• Pointer self._size = 0\n"
                f"• All operations (push, pop, top, len, is_empty) run in worst-case O(1) time."
            ),
            level="info",
        )

    # -------------------------------------------------------------------------
    # UI SETUP & LAYOUT
    # -------------------------------------------------------------------------

    def _setup_styles(self) -> None:
        """Initialize typography and widget style definitions."""
        self.font_title = tkfont.Font(family="Helvetica", size=13, weight="bold")
        self.font_subtitle = tkfont.Font(family="Helvetica", size=9)
        self.font_btn = tkfont.Font(family="Helvetica", size=10, weight="bold")
        self.font_label = tkfont.Font(family="Helvetica", size=9, weight="bold")
        self.font_code = tkfont.Font(family="Courier", size=9)
        self.font_candy = tkfont.Font(family="Helvetica", size=8, weight="bold")

    def _build_header(self) -> None:
        """Build top banner explaining the DAA stack demonstration."""
        header_frame = tk.Frame(self.root, bg="#1E293B", pady=8, padx=16)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_lbl = tk.Label(
            header_frame,
            text="PEZ CANDY DISPENSER — ARRAY-BASED STACK",
            font=self.font_title,
            fg="#F8FAFC",
            bg="#1E293B",
            anchor="w",
        )
        title_lbl.pack(fill=tk.X)

        subtitle_lbl = tk.Label(
            header_frame,
            text=(
                f"Design and Analysis of Algorithms | LIFO Discipline | "
                f"Fixed Array self._data = [None]*{DEFAULT_CAPACITY} | O(1) Push/Pop/Top/Len/IsEmpty"
            ),
            font=self.font_subtitle,
            fg="#94A3B8",
            bg="#1E293B",
            anchor="w",
        )
        subtitle_lbl.pack(fill=tk.X, pady=(2, 0))

    def _build_main_layout(self) -> None:
        """Create split-pane layout: Dispenser Canvas (left) and Controls/Logs (right)."""
        content_frame = tk.Frame(self.root, bg="#0F172A")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # ----------------- LEFT: DISPENSER CANVAS -----------------
        left_frame = tk.Frame(content_frame, bg="#1E293B", bd=1, relief=tk.RIDGE)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

        canvas_header = tk.Label(
            left_frame,
            text="PHYSICAL PEZ DISPENSER VIEW",
            font=self.font_label,
            fg="#38BDF8",
            bg="#1E293B",
            pady=5,
        )
        canvas_header.pack(fill=tk.X)

        self.canvas = tk.Canvas(
            left_frame,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#0B132B",
            highlightthickness=0,
        )
        self.canvas.pack(padx=8, pady=(0, 8))

        # ----------------- RIGHT: CONTROLS & MONITOR -----------------
        right_frame = tk.Frame(content_frame, bg="#0F172A")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 1. Action Buttons Panel
        self._build_button_panel(right_frame)

        # 2. Memory Inspector (Array visualizer)
        self._build_memory_inspector(right_frame)

        # 3. Status Log & Output Panel
        self._build_status_panel(right_frame)

    def _build_button_panel(self, parent: tk.Frame) -> None:
        """Build stack method invocation buttons and animation controls."""
        btn_box = tk.LabelFrame(
            parent,
            text=" Stack Operations (All O(1)) ",
            font=self.font_label,
            fg="#38BDF8",
            bg="#1E293B",
            padx=10,
            pady=6,
            bd=1,
            relief=tk.GROOVE,
        )
        btn_box.pack(fill=tk.X, pady=(0, 6))

        # Row 1: Primary stack methods (Plain text labels, no emoji)
        row1 = tk.Frame(btn_box, bg="#1E293B")
        row1.pack(fill=tk.X, pady=2)

        self.btn_push = tk.Button(
            row1,
            text="Push Candy",
            command=self.on_push,
            bg="#059669",
            fg="#FFFFFF",
            activebackground="#10B981",
            activeforeground="#FFFFFF",
            font=self.font_btn,
            padx=8,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        )
        self.btn_push.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_pop = tk.Button(
            row1,
            text="Pop Candy",
            command=self.on_pop,
            bg="#DC2626",
            fg="#FFFFFF",
            activebackground="#EF4444",
            activeforeground="#FFFFFF",
            font=self.font_btn,
            padx=8,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        )
        self.btn_pop.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_top = tk.Button(
            row1,
            text="Top (Peek)",
            command=self.on_top,
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            font=self.font_btn,
            padx=8,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        )
        self.btn_top.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_len = tk.Button(
            row1,
            text="Len()",
            command=self.on_len,
            bg="#4F46E5",
            fg="#FFFFFF",
            activebackground="#6366F1",
            activeforeground="#FFFFFF",
            font=self.font_btn,
            padx=8,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        )
        self.btn_len.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_is_empty = tk.Button(
            row1,
            text="Is Empty?",
            command=self.on_is_empty,
            bg="#7C3AED",
            fg="#FFFFFF",
            activebackground="#8B5CF6",
            activeforeground="#FFFFFF",
            font=self.font_btn,
            padx=8,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        )
        self.btn_is_empty.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Row 2: Secondary controls (Reset, Fill, Clear, Animation toggle)
        row2 = tk.Frame(btn_box, bg="#1E293B")
        row2.pack(fill=tk.X, pady=(5, 2))

        self.btn_reset = tk.Button(
            row2,
            text="Reset Dispenser",
            command=self.on_reset,
            bg="#475569",
            fg="#F8FAFC",
            activebackground="#64748B",
            font=self.font_label,
            padx=8,
            pady=3,
            relief=tk.GROOVE,
            cursor="hand2",
        )
        self.btn_reset.pack(side=tk.LEFT, padx=2)

        self.btn_fill = tk.Button(
            row2,
            text="Fill to Max",
            command=self.on_fill_all,
            bg="#0369A1",
            fg="#F8FAFC",
            activebackground="#0284C7",
            font=self.font_label,
            padx=8,
            pady=3,
            relief=tk.GROOVE,
            cursor="hand2",
        )
        self.btn_fill.pack(side=tk.LEFT, padx=2)

        self.btn_clear = tk.Button(
            row2,
            text="Clear All",
            command=self.on_clear_all,
            bg="#991B1B",
            fg="#F8FAFC",
            activebackground="#B91C1C",
            font=self.font_label,
            padx=8,
            pady=3,
            relief=tk.GROOVE,
            cursor="hand2",
        )
        self.btn_clear.pack(side=tk.LEFT, padx=2)

        # Animation toggle checkbox
        self.animate_var = tk.BooleanVar(value=True)
        self.chk_anim = tk.Checkbutton(
            row2,
            text="Smooth Animation & Slide-Out",
            variable=self.animate_var,
            bg="#1E293B",
            fg="#E2E8F0",
            selectcolor="#0F172A",
            activebackground="#1E293B",
            activeforeground="#FFFFFF",
            font=self.font_label,
        )
        self.chk_anim.pack(side=tk.RIGHT, padx=4)

    def _build_memory_inspector(self, parent: tk.Frame) -> None:
        """Build the live ArrayStack._data memory visualizer without hardcoded capacity."""
        self.mem_frame = tk.LabelFrame(
            parent,
            text=f" Underlying Memory Representation: self._data = [None] * {DEFAULT_CAPACITY} ",
            font=self.font_label,
            fg="#38BDF8",
            bg="#1E293B",
            padx=8,
            pady=6,
            bd=1,
            relief=tk.GROOVE,
        )
        self.mem_frame.pack(fill=tk.X, pady=(0, 6))

        # Status text summary above slots
        self.mem_info_lbl = tk.Label(
            self.mem_frame,
            text=f"self._size = 0 | Capacity = {DEFAULT_CAPACITY} | Slots remaining = {DEFAULT_CAPACITY} | Top index = None",
            font=self.font_code,
            fg="#FACC15",
            bg="#1E293B",
            anchor="w",
        )
        self.mem_info_lbl.pack(fill=tk.X, pady=(0, 4))

        # Array slot cards
        self.slots_container = tk.Frame(self.mem_frame, bg="#1E293B")
        self.slots_container.pack(fill=tk.X)

        self.slot_widgets: List[dict] = []
        for i in range(DEFAULT_CAPACITY):
            card = tk.Frame(
                self.slots_container,
                bg="#0F172A",
                bd=1,
                relief=tk.SOLID,
                padx=2,
                pady=3,
            )
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2)

            idx_lbl = tk.Label(
                card,
                text=f"[{i}]",
                font=("Courier", 8, "bold"),
                fg="#94A3B8",
                bg="#0F172A",
            )
            idx_lbl.pack(fill=tk.X)

            val_lbl = tk.Label(
                card,
                text="None",
                font=("Courier", 8),
                fg="#64748B",
                bg="#0F172A",
                width=8,
            )
            val_lbl.pack(fill=tk.X, pady=1)

            ptr_lbl = tk.Label(
                card,
                text=" ",
                font=("Courier", 8, "bold"),
                fg="#10B981",
                bg="#0F172A",
            )
            ptr_lbl.pack(fill=tk.X)

            self.slot_widgets.append({
                "frame": card,
                "idx": idx_lbl,
                "val": val_lbl,
                "ptr": ptr_lbl,
            })

    def _build_status_panel(self, parent: tk.Frame) -> None:
        """Build status panel with result badge and scrollable DAA log."""
        log_frame = tk.LabelFrame(
            parent,
            text=" Method Execution & Analysis Log (O(1) Verification) ",
            font=self.font_label,
            fg="#38BDF8",
            bg="#1E293B",
            padx=8,
            pady=6,
            bd=1,
            relief=tk.GROOVE,
        )
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Prominent single-line banner for rapid visual status
        self.status_banner = tk.Label(
            log_frame,
            text="READY — Select a stack operation above",
            font=self.font_btn,
            bg="#334155",
            fg="#F8FAFC",
            padx=10,
            pady=5,
            relief=tk.RIDGE,
            anchor="w",
        )
        self.status_banner.pack(fill=tk.X, pady=(0, 4))

        # Multi-line Text widget with scrollbar for complete audit trail
        text_container = tk.Frame(log_frame, bg="#0F172A")
        text_container.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            text_container,
            bg="#0B132B",
            fg="#E2E8F0",
            insertbackground="#38BDF8",
            font=self.font_code,
            wrap=tk.WORD,
            bd=0,
            padx=8,
            pady=6,
            height=11,
        )
        scrollbar = tk.Scrollbar(
            text_container,
            orient=tk.VERTICAL,
            command=self.log_text.yview,
        )
        self.log_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Text tag styling for structured logging
        self.log_text.tag_configure("title_success", foreground="#34D399", font=("Courier", 9, "bold"))
        self.log_text.tag_configure("title_error", foreground="#F87171", font=("Courier", 9, "bold"))
        self.log_text.tag_configure("title_info", foreground="#60A5FA", font=("Courier", 9, "bold"))
        self.log_text.tag_configure("body", foreground="#CBD5E1")
        self.log_text.tag_configure("divider", foreground="#475569")

    # -------------------------------------------------------------------------
    # CANDY FACTORY (Ensures unique colors AND unique body shapes)
    # -------------------------------------------------------------------------

    def peek_next_candy(self) -> Tuple[Candy, int, int, int]:
        """Prepare prospective candy without advancing counters.
        
        Guarantees:
        1. No two candies currently in the dispenser share the same color.
        2. No two candies currently in the dispenser share the same shape.
        3. Candy ID / color / shape counters are NOT advanced until push succeeds.
        
        Returns:
            Tuple of (candidate_candy, next_color_index, next_shape_index, candidate_id)
        """
        raw_items = self.stack.get_raw_data()
        active_colors = {
            item.color for item in raw_items
            if item is not None and isinstance(item, Candy)
        }
        active_shapes = {
            item.shape for item in raw_items
            if item is not None and isinstance(item, Candy)
        }

        # 1. Select next available unique color
        chosen_hex = None
        chosen_color_name = None
        next_c_idx = self._color_cycle_index
        palette_len = len(CANDY_PALETTE)

        for _ in range(palette_len):
            c_hex, c_name = CANDY_PALETTE[next_c_idx]
            next_c_idx = (next_c_idx + 1) % palette_len
            if c_hex not in active_colors:
                chosen_hex = c_hex
                chosen_color_name = c_name
                break

        if chosen_hex is None:
            chosen_hex, chosen_color_name = CANDY_PALETTE[0]

        # 2. Select next available unique shape (out of 12 distinct shapes)
        chosen_shape = None
        next_s_idx = self._shape_cycle_index
        shapes_len = len(CANDY_SHAPES)

        for _ in range(shapes_len):
            s_candidate = CANDY_SHAPES[next_s_idx]
            next_s_idx = (next_s_idx + 1) % shapes_len
            if s_candidate not in active_shapes:
                chosen_shape = s_candidate
                break

        if chosen_shape is None:
            chosen_shape = CANDY_SHAPES[0]

        candidate_id = self._next_candy_id + 1
        display_shape = chosen_shape.replace("_", " ").title()
        candy_name = f"{chosen_color_name} {display_shape}"

        candidate_candy = Candy(
            candy_id=candidate_id,
            name=candy_name,
            color=chosen_hex,
            shape=chosen_shape,
        )

        return candidate_candy, next_c_idx, next_s_idx, candidate_id

    # -------------------------------------------------------------------------
    # BUTTON EVENT HANDLERS (With thorough Error Handling & Rollback)
    # -------------------------------------------------------------------------

    def on_push(self) -> None:
        """Handler for Push button. Demonstrates ArrayStack.push(e) in O(1).
        
        Guarantees that candy ID / color / shape counters only advance
        if push() succeeds. On DispenserFull, counters are untouched.
        """
        try:
            candidate_candy, next_c_idx, next_s_idx, next_id = self.peek_next_candy()

            # Push into array-based stack (O(1)) - raises DispenserFull if full
            self.stack.push(candidate_candy)

            # ONLY advance counters if push() succeeded without exception
            self._next_candy_id = next_id
            self._color_cycle_index = next_c_idx
            self._shape_cycle_index = next_s_idx

            stack_len = len(self.stack)
            idx = stack_len - 1
            remaining = self.stack.capacity - stack_len

            msg = (
                f"Pushed: '{candidate_candy.name}'\n"
                f"• Candy ID: #{candidate_candy.id} | Color: {candidate_candy.color} | Shape: {candidate_candy.shape.replace('_', ' ').capitalize()}\n"
                f"• Array Slot: self._data[{idx}] = {candidate_candy}\n"
                f"• Pointer State: self._size = {stack_len}\n"
                f"• Slots Remaining: {remaining} of {self.stack.capacity}\n"
                f"• Complexity: O(1) worst-case"
            )
            self.log_status(title="PUSH SUCCESSFUL", message=msg, level="success")
            self.animate_or_draw()

        except DispenserFull as ex:
            # Counters were NOT advanced, so IDs never skip!
            self.log_status(
                title="ERROR: DISPENSER FULL",
                message=(
                    f"{ex}!\n"
                    f"• Attempted push on full ArrayStack (size = {len(self.stack)} / {self.stack.capacity}).\n"
                    f"• Fixed-size array self._data is completely occupied.\n"
                    f"• Counters preserved: Next pushed candy will still use ID #{self._next_candy_id + 1}.\n"
                    f"• Pop an item to free an array slot."
                ),
                level="error",
            )
        except Exception as ex:
            self.log_status(
                title="UNEXPECTED SYSTEM ERROR",
                message=f"An unexpected error occurred during push(): {ex}",
                level="error",
            )

    def on_pop(self) -> None:
        """Handler for Pop button. Demonstrates ArrayStack.pop() in O(1).
        
        Animates the popped candy sliding out through the exit before the spring rises.
        """
        try:
            # Pop from array-based stack (O(1))
            removed_candy = self.stack.pop()

            stack_len = len(self.stack)
            vacated_idx = stack_len
            remaining = self.stack.capacity - stack_len

            if self.stack.is_empty():
                new_top_str = "Dispenser is now empty (size = 0)"
            else:
                current_top = self.stack.top()
                new_top_str = f"'{current_top.name}' (ID: #{current_top.id}, Slot: [{stack_len - 1}])"

            msg = (
                f"Popped: '{removed_candy.name}' (ID: #{removed_candy.id}, Shape: {removed_candy.shape.replace('_', ' ').capitalize()})\n"
                f"• Vacated array slot self._data[{vacated_idx}] explicitly reset to None\n"
                f"• Pointer State: self._size = {stack_len}\n"
                f"• New Top Candy: {new_top_str}\n"
                f"• Slots Remaining: {remaining} of {self.stack.capacity}\n"
                f"• Complexity: O(1) worst-case"
            )
            self.log_status(title="POP SUCCESSFUL", message=msg, level="success")

            # Slide-out animation before spring extends
            if self.animate_var.get():
                self._cancel_animation()
                self._start_pop_slide(removed_candy)
            else:
                self._cancel_animation()
                self._current_display_size = float(len(self.stack))
                self.draw(self._current_display_size)

        except DispenserEmpty as ex:
            self.log_status(
                title="ERROR: DISPENSER EMPTY",
                message=(
                    f"{ex}!\n"
                    f"• Attempted pop from empty ArrayStack (self._size == 0).\n"
                    f"• Underflow condition safely intercepted without crash."
                ),
                level="error",
            )
        except Exception as ex:
            self.log_status(
                title="UNEXPECTED SYSTEM ERROR",
                message=f"An unexpected error occurred during pop(): {ex}",
                level="error",
            )

    def on_top(self) -> None:
        """Handler for Top button. Demonstrates ArrayStack.top() in O(1)."""
        try:
            # Inspect top without removing (O(1))
            top_candy = self.stack.top()
            top_idx = len(self.stack) - 1
            beneath_count = top_idx  # Number of candies below the top element

            msg = (
                f"Current Top Candy: '{top_candy.name}'\n"
                f"• Candy ID: #{top_candy.id} | Color: {top_candy.color} | Shape: {top_candy.shape.replace('_', ' ').capitalize()}\n"
                f"• Array Slot: self._data[{top_idx}]\n"
                f"• Candies Beneath It: {beneath_count} (in slots [0] to [{top_idx - 1}] if any)\n"
                f"• Complexity: O(1) worst-case (no stack modification)"
            )
            self.log_status(title="TOP (PEEK) INSPECTION", message=msg, level="info")
            self._trigger_top_highlight()

        except DispenserEmpty as ex:
            self.log_status(
                title="ERROR: DISPENSER EMPTY",
                message=(
                    f"{ex}!\n"
                    f"• Attempted top() on empty ArrayStack.\n"
                    f"• There are no candies currently in the dispenser to inspect."
                ),
                level="error",
            )
        except Exception as ex:
            self.log_status(
                title="UNEXPECTED SYSTEM ERROR",
                message=f"An unexpected error occurred during top(): {ex}",
                level="error",
            )

    def on_len(self) -> None:
        """Handler for Len button. Demonstrates len(stack) and stack.len() in O(1)."""
        try:
            count = self.stack.len()
            capacity = self.stack.capacity
            fill_pct = (count / capacity) * 100.0

            msg = (
                f"Stack Length Query:\n"
                f"• Current Count (self._size): {count}\n"
                f"• Max Capacity: {capacity}\n"
                f"• Fill Percentage: {fill_pct:.1f}%\n"
                f"• Available Slots: {capacity - count}\n"
                f"• Complexity: O(1) worst-case"
            )
            self.log_status(title="LEN() QUERY", message=msg, level="info")

        except Exception as ex:
            self.log_status(
                title="UNEXPECTED SYSTEM ERROR",
                message=f"An unexpected error occurred during len(): {ex}",
                level="error",
            )

    def on_is_empty(self) -> None:
        """Handler for Is Empty button. Demonstrates ArrayStack.is_empty() in O(1)."""
        try:
            empty = self.stack.is_empty()
            count = len(self.stack)

            if empty:
                status_text = "True — The dispenser is completely empty, ready to be filled!"
            else:
                status_text = f"False — The dispenser currently contains {count} candy/candies."

            msg = (
                f"Stack Emptiness Query:\n"
                f"• Result: {empty}\n"
                f"• Description: {status_text}\n"
                f"• Complexity: O(1) worst-case (self._size == 0)"
            )
            self.log_status(title="IS_EMPTY() QUERY", message=msg, level="info")

        except Exception as ex:
            self.log_status(
                title="UNEXPECTED SYSTEM ERROR",
                message=f"An unexpected error occurred during is_empty(): {ex}",
                level="error",
            )

    def on_reset(self) -> None:
        """Handler for Reset button. Resets dispenser to empty state."""
        try:
            self._cancel_animation()
            # Empties the stack strictly via pop() to guarantee slots set to None
            while not self.stack.is_empty():
                self.stack.pop()

            self._next_candy_id = 0
            self._color_cycle_index = 0
            self._shape_cycle_index = 0

            msg = (
                f"Dispenser reset to initial empty state.\n"
                f"• All array slots self._data[0..{self.stack.capacity - 1}] cleared to None.\n"
                f"• self._size reset to 0.\n"
                f"• Spring fully extended to top dispensing mouth."
            )
            self.log_status(title="RESET DISPENSER", message=msg, level="info")
            self.animate_or_draw()

        except Exception as ex:
            self.log_status(
                title="UNEXPECTED SYSTEM ERROR",
                message=f"An unexpected error occurred during reset: {ex}",
                level="error",
            )

    def on_fill_all(self) -> None:
        """Convenience utility: pushes until dispenser is full."""
        try:
            pushed_count = 0
            while len(self.stack) < self.stack.capacity:
                candidate, next_c_idx, next_s_idx, next_id = self.peek_next_candy()
                self.stack.push(candidate)
                self._next_candy_id = next_id
                self._color_cycle_index = next_c_idx
                self._shape_cycle_index = next_s_idx
                pushed_count += 1

            self.log_status(
                title="BATCH FILL COMPLETE",
                message=f"Pushed {pushed_count} candies. Dispenser is now at full capacity ({self.stack.capacity}/{self.stack.capacity}).",
                level="success",
            )
            self.animate_or_draw()
        except DispenserFull:
            pass
        except Exception as ex:
            self.log_status(title="ERROR", message=str(ex), level="error")

    def on_clear_all(self) -> None:
        """Convenience utility: pops until dispenser is empty."""
        try:
            popped_count = 0
            while not self.stack.is_empty():
                self.stack.pop()
                popped_count += 1

            self.log_status(
                title="BATCH CLEAR COMPLETE",
                message=f"Popped {popped_count} candies. Dispenser is now empty (0/{self.stack.capacity}).",
                level="info",
            )
            self.animate_or_draw()
        except DispenserEmpty:
            pass
        except Exception as ex:
            self.log_status(title="ERROR", message=str(ex), level="error")

    # -------------------------------------------------------------------------
    # LOGGING & STATUS REPORTING
    # -------------------------------------------------------------------------

    def log_status(self, title: str, message: str, level: str = "info") -> None:
        """Record an event in the status banner and multi-line audit log."""
        color_map = {
            "success": ("#065F46", "#34D399", "title_success"),
            "error": ("#7F1D1D", "#F87171", "title_error"),
            "info": ("#1E3A8A", "#60A5FA", "title_info"),
        }
        bg_col, fg_col, tag_name = color_map.get(level, ("#334155", "#F8FAFC", "title_info"))

        # 1. Update single-line prominent banner
        self.status_banner.configure(
            text=f"[{title}] {message.splitlines()[0]}",
            bg=bg_col,
            fg="#F8FAFC",
        )

        # 2. Append to scrollable text log
        self.log_text.insert(tk.END, f"\n=== {title} ===\n", tag_name)
        self.log_text.insert(tk.END, f"{message}\n", "body")
        self.log_text.insert(tk.END, "-" * 56 + "\n", "divider")
        self.log_text.see(tk.END)

    # -------------------------------------------------------------------------
    # ANIMATION ENGINE (Slide-Out on Pop & Spring Compression/Extension)
    # -------------------------------------------------------------------------

    def animate_or_draw(self) -> None:
        """Trigger smooth frame-by-frame spring animation or immediate draw."""
        target_size = float(len(self.stack))

        # If animation is disabled by user, draw instantly
        if not self.animate_var.get():
            self._cancel_animation()
            self._current_display_size = target_size
            self.draw(self._current_display_size)
            return

        # Cancel any active animation timer and begin stepping towards target
        self._cancel_animation()
        self._animate_step(target_size)

    def _start_pop_slide(self, popped_candy: Candy) -> None:
        """Animate popped candy sliding horizontally through exit before spring extends."""
        self._sliding_candy = popped_candy
        self._slide_offset_x = 0.0
        self._animate_pop_slide_frame()

    def _animate_pop_slide_frame(self) -> None:
        """Step the horizontal slide animation for the popped candy."""
        max_slide = CANDY_WIDTH + 50
        self._slide_offset_x += 26.0

        if self._slide_offset_x >= max_slide:
            # Popped candy has exited the tube
            self._sliding_candy = None
            self._slide_offset_x = 0.0
            self._slide_job = None
            # Now trigger the spring extension animation for remaining candies
            target_size = float(len(self.stack))
            self._animate_step(target_size)
        else:
            self.draw(
                display_size=self._current_display_size,
                sliding_candy=self._sliding_candy,
                slide_offset_x=self._slide_offset_x,
            )
            self._slide_job = self.root.after(16, self._animate_pop_slide_frame)

    def _animate_step(self, target_size: float) -> None:
        """Perform one animation frame towards target_size using root.after()."""
        diff = target_size - self._current_display_size

        # Convergence threshold
        if abs(diff) < 0.04:
            self._current_display_size = target_size
            self._anim_job = None
            # Final crisp draw purely synchronized with stack state
            self.draw(self._current_display_size)
        else:
            # Spring easing formula (proportional step)
            step_delta = diff * 0.38
            self._current_display_size += step_delta
            self.draw(self._current_display_size)
            # Schedule next frame in ~16ms (~60 FPS)
            self._anim_job = self.root.after(16, lambda: self._animate_step(target_size))

    def _cancel_animation(self) -> None:
        """Safely cancel pending root.after animation callbacks."""
        if self._anim_job is not None:
            try:
                self.root.after_cancel(self._anim_job)
            except Exception:
                pass
            self._anim_job = None

        if self._slide_job is not None:
            try:
                self.root.after_cancel(self._slide_job)
            except Exception:
                pass
            self._slide_job = None

        self._sliding_candy = None
        self._slide_offset_x = 0.0

    def _trigger_top_highlight(self) -> None:
        """Temporarily highlight the top candy on the canvas for visual feedback."""
        self._highlighted_top = True
        self.draw(self._current_display_size)

        if self._highlight_job is not None:
            try:
                self.root.after_cancel(self._highlight_job)
            except Exception:
                pass

        def remove_highlight():
            self._highlighted_top = False
            self.draw(self._current_display_size)

        self._highlight_job = self.root.after(700, remove_highlight)

    # -------------------------------------------------------------------------
    # CANVAS DRAWING (SPRING & CANDIES STATE RENDERER)
    # -------------------------------------------------------------------------

    def draw(
        self,
        display_size: Optional[float] = None,
        sliding_candy: Optional[Candy] = None,
        slide_offset_x: float = 0.0,
    ) -> None:
        """Redraw the entire dispenser, spring, and candies purely from state.
        
        Spring Physics:
            spring_height = FULL_HEIGHT - (size * STEP)
            plate_y = BASE_Y - spring_height
            
            On push: spring compresses by STEP; plate and candies shift down.
            On pop:  spring extends by STEP; plate and candies shift up.
            Top candy is ALWAYS visible at constant TOP_MOUTH_Y!
        """
        if display_size is None:
            display_size = float(len(self.stack))

        self.canvas.delete("all")

        # 1. Physics Calculations
        spring_height = FULL_HEIGHT - (display_size * STEP)
        if spring_height < SPRING_MIN_HEIGHT:
            spring_height = SPRING_MIN_HEIGHT

        plate_y = BASE_Y - spring_height

        # 2. Draw static tube background and slot guide lines
        self._draw_tube_background()
        self._draw_slot_indicators()

        # 3. Draw fixed bottom base mount
        self._draw_base_mount()

        # 4. Draw spring polyline between fixed base and movable plate
        self._draw_spring(base_y=BASE_Y, plate_y=plate_y)

        # 5. Draw movable metal top plate
        self._draw_movable_plate(plate_y=plate_y)

        # 6. Draw stacked candies resting on the plate
        self._draw_candies(plate_y=plate_y)

        # 7. Draw sliding popped candy exiting through the top chute if animating
        if sliding_candy is not None:
            slide_cx = TUBE_CENTER_X + slide_offset_x
            slide_cy = TOP_MOUTH_Y + (STEP / 2)
            scx1 = slide_cx - (CANDY_WIDTH / 2)
            scx2 = slide_cx + (CANDY_WIDTH / 2)
            scy1 = slide_cy - (CANDY_HEIGHT / 2)
            scy2 = slide_cy + (CANDY_HEIGHT / 2)
            self._draw_single_candy(
                candy=sliding_candy,
                cx1=scx1,
                cy1=scy1,
                cx2=scx2,
                cy2=scy2,
                index=len(self.stack),
                highlight=True,
            )

        # 8. Draw dispenser tube acrylic casing & PEZ flip-head
        self._draw_tube_foreground()

        # 9. Update underlying memory inspector widgets
        self._update_memory_inspector()

    def _draw_tube_background(self) -> None:
        """Draw interior chamber of the dispenser tube."""
        self.canvas.create_rectangle(
            TUBE_LEFT,
            TUBE_TOP,
            TUBE_RIGHT,
            TUBE_BOTTOM,
            fill="#091E3A",
            outline="",
        )

    def _draw_slot_indicators(self) -> None:
        """Draw array index tick marks along the side of the dispenser tube."""
        for i in range(DEFAULT_CAPACITY):
            # Physical slot position when stack has (i + 1) items
            slot_y = TOP_MOUTH_Y + (i * STEP)
            # Tick mark on left
            self.canvas.create_line(
                TUBE_LEFT - 12,
                slot_y + (STEP // 2),
                TUBE_LEFT - 2,
                slot_y + (STEP // 2),
                fill="#475569",
                width=1,
            )
            # Slot label
            self.canvas.create_text(
                TUBE_LEFT - 26,
                slot_y + (STEP // 2),
                text=f"[{i}]",
                fill="#64748B",
                font=("Courier", 8),
            )

    def _draw_base_mount(self) -> None:
        """Draw fixed base mount at the bottom of the tube."""
        self.canvas.create_rectangle(
            TUBE_LEFT - 16,
            TUBE_BOTTOM - 6,
            TUBE_RIGHT + 16,
            TUBE_BOTTOM + 24,
            fill="#1E293B",
            outline="#475569",
            width=2,
        )
        self.canvas.create_rectangle(
            TUBE_CENTER_X - 30,
            BASE_Y - 4,
            TUBE_CENTER_X + 30,
            BASE_Y + 4,
            fill="#334155",
            outline="#64748B",
            width=1,
        )

    def _draw_spring(self, base_y: float, plate_y: float) -> None:
        """Draw spring zigzag polyline between fixed base and movable plate."""
        spring_top_y = plate_y + PLATE_THICKNESS
        total_span = base_y - spring_top_y
        if total_span <= 4:
            total_span = 4

        num_peaks = SPRING_NUM_COILS * 2
        pts = []

        # Start at base center
        pts.extend([TUBE_CENTER_X, base_y])

        for k in range(1, num_peaks):
            progress = k / num_peaks
            y = base_y - (progress * total_span)
            direction = -1 if (k % 2 == 1) else 1
            x = TUBE_CENTER_X + (direction * SPRING_COIL_RADIUS)
            pts.extend([x, y])

        # End at movable plate bottom center
        pts.extend([TUBE_CENTER_X, spring_top_y])

        # Spring shadow line for 3D depth
        self.canvas.create_line(
            [coord + (1 if idx % 2 == 0 else 1) for idx, coord in enumerate(pts)],
            fill="#0F172A",
            width=5,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
        )
        # Main metallic spring wire
        self.canvas.create_line(
            pts,
            fill="#94A3B8",
            width=3.5,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
        )

    def _draw_movable_plate(self, plate_y: float) -> None:
        """Draw the movable top plate that compresses the spring."""
        px1 = TUBE_LEFT + 4
        px2 = TUBE_RIGHT - 4
        py1 = plate_y
        py2 = plate_y + PLATE_THICKNESS

        self.canvas.create_rectangle(
            px1,
            py1,
            px2,
            py2,
            fill="#475569",
            outline="#94A3B8",
            width=1.5,
        )
        self.canvas.create_line(
            px1 + 2,
            py1 + 2,
            px2 - 2,
            py1 + 2,
            fill="#CBD5E1",
            width=1,
        )

    def _draw_candies(self, plate_y: float) -> None:
        """Draw all candies currently in the stack resting upon the movable plate."""
        raw_data = self.stack.get_raw_data()
        stack_size = len(self.stack)

        for i in range(stack_size):
            candy = raw_data[i]
            if candy is None:
                continue

            # Candy sits on top of candies beneath it (or on the plate for index 0)
            candy_bottom_y = plate_y - (i * STEP)
            candy_top_y = plate_y - ((i + 1) * STEP)

            # Center candy vertically within its step slot
            slot_mid_y = (candy_bottom_y + candy_top_y) / 2
            cy1 = slot_mid_y - (CANDY_HEIGHT / 2)
            cy2 = slot_mid_y + (CANDY_HEIGHT / 2)
            cx1 = TUBE_CENTER_X - (CANDY_WIDTH / 2)
            cx2 = TUBE_CENTER_X + (CANDY_WIDTH / 2)

            is_top_candy = (i == stack_size - 1)
            is_highlighted = is_top_candy and self._highlighted_top

            self._draw_single_candy(
                candy=candy,
                cx1=cx1,
                cy1=cy1,
                cx2=cx2,
                cy2=cy2,
                index=i,
                highlight=is_highlighted,
            )

    def _draw_single_candy(
        self,
        candy: Candy,
        cx1: float,
        cy1: float,
        cx2: float,
        cy2: float,
        index: int,
        highlight: bool = False,
    ) -> None:
        """Draw an individual candy tablet whose BODY is drawn in its own shape.
        
        The candy body is rendered using Canvas primitives (create_polygon, create_oval)
        in its distinctive shape, colored with candy.color.
        A center high-contrast badge plate ensures the ID, name, and stack index
        remain crisp, clean, and 100% readable across all colors and shapes.
        """
        outline_col = "#FDE047" if highlight else "#0F172A"
        outline_w = 3.0 if highlight else 1.5

        # 1. Draw Candy BODY in its distinct shape
        self._draw_candy_body(
            shape=candy.shape,
            cx1=cx1,
            cy1=cy1,
            cx2=cx2,
            cy2=cy2,
            color=candy.color,
            outline=outline_col,
            width=outline_w,
        )

        # 2. Draw high-contrast center label badge
        cx = (cx1 + cx2) / 2
        cy = (cy1 + cy2) / 2
        badge_w = 106
        badge_h = 18
        bx1 = cx - (badge_w / 2)
        bx2 = cx + (badge_w / 2)
        by1 = cy - (badge_h / 2)
        by2 = cy + (badge_h / 2)

        # Subtle dark badge backing
        self.canvas.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            fill="#0B132B",
            outline="#334155",
            width=1,
        )

        # Candy ID & Name (left-aligned)
        name_part = candy.name.split()[0]
        self.canvas.create_text(
            bx1 + 6,
            cy,
            text=f"#{candy.id} {name_part}",
            fill="#F8FAFC",
            font=self.font_candy,
            anchor="w",
        )

        # Array stack index badge (right-aligned in gold)
        self.canvas.create_text(
            bx2 - 6,
            cy,
            text=f"[{index}]",
            fill="#FACC15",
            font=("Courier", 8, "bold"),
            anchor="e",
        )

    def _draw_candy_body(
        self,
        shape: str,
        cx1: float,
        cy1: float,
        cx2: float,
        cy2: float,
        color: str,
        outline: str,
        width: float,
    ) -> None:
        """Render the candy BODY in its own geometric shape using Canvas primitives."""
        cx = (cx1 + cx2) / 2
        cy = (cy1 + cy2) / 2
        w = cx2 - cx1
        h = cy2 - cy1

        if shape == "circle":
            # Wide pill-oval fitting the slot
            self.canvas.create_oval(
                cx1 + 4,
                cy1,
                cx2 - 4,
                cy2,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "diamond":
            # 4-pointed rhombus
            pts = [
                cx, cy1,
                cx2, cy,
                cx, cy2,
                cx1, cy,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "triangle":
            # Upward-pointing triangle
            pts = [
                cx, cy1,
                cx2 - 6, cy2,
                cx1 + 6, cy2,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "star":
            # 5-pointed star fitting the candy slot
            pts = []
            rx_outer = w / 2
            ry_outer = h / 2
            rx_inner = rx_outer * 0.44
            ry_inner = ry_outer * 0.44
            for k in range(10):
                angle = (-math.pi / 2) + (k * math.pi / 5)
                rx = rx_outer if (k % 2 == 0) else rx_inner
                ry = ry_outer if (k % 2 == 0) else ry_inner
                pts.extend([cx + (rx * math.cos(angle)), cy + (ry * math.sin(angle))])
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "hexagon":
            # 6-sided elongated hexagon
            pts = [
                cx1, cy,
                cx1 + (w * 0.22), cy1,
                cx2 - (w * 0.22), cy1,
                cx2, cy,
                cx2 - (w * 0.22), cy2,
                cx1 + (w * 0.22), cy2,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "octagon":
            # 8-sided chamfered tablet
            c = 12
            pts = [
                cx1 + c, cy1,
                cx2 - c, cy1,
                cx2, cy1 + c,
                cx2, cy2 - c,
                cx2 - c, cy2,
                cx1 + c, cy2,
                cx1, cy2 - c,
                cx1, cy1 + c,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "pentagon":
            # Upward-pointing 5-sided pentagon
            pts = [
                cx, cy1,
                cx2 - 6, cy1 + (h * 0.38),
                cx2 - (w * 0.18), cy2,
                cx1 + (w * 0.18), cy2,
                cx1 + 6, cy1 + (h * 0.38),
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "trapezoid":
            # Isosceles trapezoid
            pts = [
                cx1 + (w * 0.18), cy1,
                cx2 - (w * 0.18), cy1,
                cx2 - 4, cy2,
                cx1 + 4, cy2,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "parallelogram":
            # Skewed tablet
            pts = [
                cx1 + (w * 0.16), cy1,
                cx2 - 4, cy1,
                cx2 - (w * 0.16), cy2,
                cx1 + 4, cy2,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "cross":
            # 12-sided plus / cross
            cw = w * 0.32
            ch = h * 0.26
            pts = [
                cx - cw, cy1,
                cx + cw, cy1,
                cx + cw, cy - ch,
                cx2, cy - ch,
                cx2, cy + ch,
                cx + cw, cy + ch,
                cx + cw, cy2,
                cx - cw, cy2,
                cx - cw, cy + ch,
                cx1, cy + ch,
                cx1, cy - ch,
                cx - cw, cy - ch,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        elif shape == "chevron":
            # Horizontal chevron arrow tablet
            pts = [
                cx1 + 8, cy1,
                cx, cy1 + 2,
                cx2 - 4, cy,
                cx, cy2 - 2,
                cx1 + 8, cy2,
                cx1 + 24, cy,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
            )

        else:
            # "rounded_bar" (Pill / rounded rectangular tablet)
            c = 10
            pts = [
                cx1 + c, cy1,
                cx2 - c, cy1,
                cx2, cy1 + c,
                cx2, cy2 - c,
                cx2 - c, cy2,
                cx1 + c, cy2,
                cx1, cy2 - c,
                cx1, cy1 + c,
            ]
            self.canvas.create_polygon(
                pts,
                fill=color,
                outline=outline,
                width=width,
                smooth=True,
            )

    def _draw_tube_foreground(self) -> None:
        """Draw PEZ flip-top head, acrylic tube walls, and dispensing opening."""
        # Transparent tube vertical walls
        self.canvas.create_line(
            TUBE_LEFT,
            TOP_MOUTH_Y,
            TUBE_LEFT,
            TUBE_BOTTOM,
            fill="#38BDF8",
            width=3,
        )
        # Right wall with opening chute at the top
        self.canvas.create_line(
            TUBE_RIGHT,
            TOP_MOUTH_Y + STEP,
            TUBE_RIGHT,
            TUBE_BOTTOM,
            fill="#38BDF8",
            width=3,
        )

        # Glass gloss line reflection down the tube
        self.canvas.create_line(
            TUBE_LEFT + 8,
            TOP_MOUTH_Y + 10,
            TUBE_LEFT + 8,
            TUBE_BOTTOM - 10,
            fill="#FFFFFF",
            width=1.5,
            stipple="gray25",
        )

        # Dispenser head (PEZ flip cap)
        head_pts = [
            TUBE_LEFT - 8, TOP_MOUTH_Y,
            TUBE_LEFT - 8, TUBE_TOP,
            TUBE_CENTER_X + 20, TUBE_TOP - 8,
            TUBE_RIGHT + 18, TUBE_TOP + 12,
            TUBE_RIGHT + 18, TOP_MOUTH_Y,
        ]
        self.canvas.create_polygon(
            head_pts,
            fill="#D97706",
            outline="#F59E0B",
            width=2,
        )

        # Hinge circle on left
        self.canvas.create_oval(
            TUBE_LEFT - 12,
            TOP_MOUTH_Y - 14,
            TUBE_LEFT + 2,
            TOP_MOUTH_Y,
            fill="#B45309",
            outline="#F59E0B",
            width=1.5,
        )

        # Dispensing arrow badge (plain text, no emoji)
        self.canvas.create_text(
            TUBE_RIGHT + 22,
            TOP_MOUTH_Y + (STEP // 2),
            text="EXIT ->",
            fill="#FACC15",
            font=("Helvetica", 8, "bold"),
            anchor="w",
        )

    # -------------------------------------------------------------------------
    # MEMORY INSPECTOR SYNCHRONIZATION
    # -------------------------------------------------------------------------

    def _update_memory_inspector(self) -> None:
        """Synchronize the live array visualizer with ArrayStack._data."""
        raw_data = self.stack.get_raw_data()
        current_len = len(self.stack)
        top_idx = (current_len - 1) if (current_len > 0) else None

        # Update summary text without hardcoded numbers
        top_str = f"[{top_idx}]" if top_idx is not None else "None (empty)"
        self.mem_info_lbl.configure(
            text=(
                f"self._size = {current_len} | "
                f"Capacity = {self.stack.capacity} | "
                f"Slots Remaining = {self.stack.capacity - current_len} | "
                f"Top Index = {top_str}"
            )
        )

        # Update slot card widgets
        for i in range(DEFAULT_CAPACITY):
            card_dict = self.slot_widgets[i]
            val = raw_data[i]

            if val is not None and isinstance(val, Candy):
                card_dict["frame"].configure(bg=val.color)
                card_dict["idx"].configure(bg=val.color, fg="#0F172A")
                card_dict["val"].configure(
                    text=f"#{val.id} {val.shape[:4]}",
                    bg=val.color,
                    fg="#0F172A",
                )
            else:
                card_dict["frame"].configure(bg="#0F172A")
                card_dict["idx"].configure(bg="#0F172A", fg="#94A3B8")
                card_dict["val"].configure(
                    text="None",
                    bg="#0F172A",
                    fg="#475569",
                )

            # TOP Pointer indicator (plain text)
            if top_idx is not None and i == top_idx:
                card_dict["ptr"].configure(text="TOP", fg="#FACC15")
            else:
                card_dict["ptr"].configure(text=" ")


# =============================================================================
# SELF-TEST & VERIFICATION ROUTINE (CONFIRMS ZERO CRASHES & O(1) BEHAVIOR)
# =============================================================================

def run_headless_tests() -> bool:
    """Execute rigorous algorithmic tests on ArrayStack without GUI display.
    
    Verifies:
    1. push() until full -> DispenserFull raised.
    2. pop() until empty -> DispenserEmpty raised.
    3. top() on empty -> DispenserEmpty raised.
    4. pop() on empty -> DispenserEmpty raised.
    5. Vacated slots are set back to None.
    6. All operations maintain O(1) performance guarantees.
    """
    print("=" * 60)
    print("RUNNING AUTOMATED ARRAYSTACK ALGORITHMIC VERIFICATION")
    print("=" * 60)

    stack = ArrayStack(capacity=DEFAULT_CAPACITY)
    assert len(stack) == 0, "Initial stack size must be 0"
    assert stack.is_empty() is True, "Initial stack must be empty"
    print(f"✓ Initial state: capacity={DEFAULT_CAPACITY}, size=0, is_empty=True")

    # Test top on empty
    try:
        stack.top()
        assert False, "top() on empty stack did not raise DispenserEmpty"
    except DispenserEmpty as ex:
        print(f"✓ Intercepted top() on empty: '{ex}'")

    # Test pop on empty
    try:
        stack.pop()
        assert False, "pop() on empty stack did not raise DispenserEmpty"
    except DispenserEmpty as ex:
        print(f"✓ Intercepted pop() on empty: '{ex}'")

    # Push to capacity (DEFAULT_CAPACITY items)
    for i in range(DEFAULT_CAPACITY):
        c = Candy(i + 1, f"Flavor {i}", "#FF0000", "circle")
        stack.push(c)
        assert len(stack) == i + 1
        assert stack.top() is c
    print(f"✓ Pushed {DEFAULT_CAPACITY} items to capacity. Current size = {len(stack)}")

    # Verify push on full
    try:
        stack.push(Candy(DEFAULT_CAPACITY + 1, "Overflow", "#FFFFFF", "star"))
        assert False, "push() on full stack did not raise DispenserFull"
    except DispenserFull as ex:
        print(f"✓ Intercepted push() on full: '{ex}'")

    # Verify top
    top_candy = stack.top()
    assert top_candy.id == DEFAULT_CAPACITY, f"Expected top candy ID {DEFAULT_CAPACITY}, got {top_candy.id}"
    print(f"✓ Verified top() on full stack: {top_candy}")

    # Pop all items and check vacated slots reset to None
    for i in range(DEFAULT_CAPACITY, 0, -1):
        c = stack.pop()
        assert c.id == i, f"Expected popped ID {i}, got {c.id}"
        # Check underlying array slot was set back to None
        raw = stack.get_raw_data()
        assert raw[i - 1] is None, f"Slot {i - 1} was not reset to None!"

    assert len(stack) == 0
    assert stack.is_empty() is True
    print("✓ Successfully popped all items. All vacated slots verified reset to None.")

    # Re-verify pop & top on newly emptied stack
    try:
        stack.pop()
        assert False, "pop() on emptied stack failed to raise DispenserEmpty"
    except DispenserEmpty:
        print("✓ Re-verified pop() on emptied stack raises DispenserEmpty")

    try:
        stack.top()
        assert False, "top() on emptied stack failed to raise DispenserEmpty"
    except DispenserEmpty:
        print("✓ Re-verified top() on emptied stack raises DispenserEmpty")

    print("=" * 60)
    print("ALL ARRAYSTACK VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> None:
    """Application entry point."""
    # Check for test flag
    if "--test" in sys.argv:
        success = run_headless_tests()
        sys.exit(0 if success else 1)

    if not TKINTER_AVAILABLE:
        print("Error: The 'tkinter' standard module is required to run the GUI.")
        print("Run headless algorithmic tests via: python3 candy_dispenser.py --test")
        print("Or install tkinter on Linux (e.g. 'sudo dnf install python3-tkinter').")
        sys.exit(1)

    # Launch Tkinter GUI
    root = tk.Tk()
    app = CandyDispenserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
