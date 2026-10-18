"""Interactive Hamming(7, 4) code demonstrator."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


BIT_LABELS = {
    1: "P1",
    2: "P2",
    3: "D1",
    4: "P4",
    5: "D2",
    6: "D3",
    7: "D4",
}
PARITY_SETS = {
    1: (1, 3, 5, 7),
    2: (2, 3, 6, 7),
    4: (4, 5, 6, 7),
}


def _validate_bits(value: str, length: int, label: str) -> str:
    bits = value.strip()
    if len(bits) != length or any(bit not in "01" for bit in bits):
        raise ValueError(f"{label} must contain exactly {length} bits (0 or 1).")
    return bits


def encode_hamming(data_bits: str) -> str:
    """Encode D4 D3 D2 D1 as a Hamming(7, 4) word with even parity."""
    data = _validate_bits(data_bits, 4, "Original message")
    d4, d3, d2, d1 = (int(bit) for bit in data)
    code = [0] * 8
    code[3], code[5], code[6], code[7] = d1, d2, d3, d4
    code[1] = code[3] ^ code[5] ^ code[7]
    code[2] = code[3] ^ code[6] ^ code[7]
    code[4] = code[5] ^ code[6] ^ code[7]
    return "".join(str(code[position]) for position in range(1, 8))


def calculate_syndrome(received_bits: str) -> tuple[int, dict[int, int]]:
    """Return the faulty position (0 means none) and each parity check result."""
    received = _validate_bits(received_bits, 7, "Received message")
    bits = [0] + [int(bit) for bit in received]
    checks = {
        parity_position: _xor(bits[position] for position in covered_positions)
        for parity_position, covered_positions in PARITY_SETS.items()
    }
    error_position = sum(
        parity_position for parity_position, failed in checks.items() if failed
    )
    return error_position, checks


def correct_single_bit(received_bits: str, error_position: int) -> str:
    """Correct the indicated bit in a 7-bit word, or return it unchanged at 0."""
    received = _validate_bits(received_bits, 7, "Received message")
    if not 0 <= error_position <= 7:
        raise ValueError("Error position must be between 0 and 7.")
    if error_position == 0:
        return received
    corrected = list(received)
    corrected[error_position - 1] = "1" if corrected[error_position - 1] == "0" else "0"
    return "".join(corrected)


def extract_data(codeword: str) -> str:
    """Extract D4 D3 D2 D1 from a Hamming(7, 4) word."""
    code = _validate_bits(codeword, 7, "Codeword")
    return "".join(code[position - 1] for position in (7, 6, 5, 3))


def _xor(values: Iterable[int]) -> int:
    result = 0
    for value in values:
        result ^= value
    return result


class HammingDemo:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Hamming Code Demonstrator")
        self.root.geometry("820x760")
        self.root.minsize(760, 700)
        self.root.configure(bg="#f3f5f9")
        self.logo_image = tk.PhotoImage(
            file=str(Path(__file__).with_name("logo.png"))
        ).subsample(2, 2)

        self.data_var = tk.StringVar(value="1011")
        self.received_var = tk.StringVar()
        self.flip_position_var = tk.StringVar(value="1")
        self.result_var = tk.StringVar(value="Encode a message to begin.")
        self.checks_var = tk.StringVar(value="Parity checks: —")
        self.corrected_var = tk.StringVar(value="Corrected code: —")
        self.recovered_var = tk.StringVar(value="Recovered data: —")
        self.original_word = ""

        self._configure_style()
        self._build_layout()
        self.encode_message()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f3f5f9")
        style.configure("TLabel", background="#f3f5f9", foreground="#263248")
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#17365d")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#53647a")
        style.configure("Section.TLabelframe", background="#ffffff", padding=14)
        style.configure(
            "Section.TLabelframe.Label",
            background="#ffffff",
            foreground="#17365d",
            font=("Segoe UI", 11, "bold"),
        )
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TButton", padding=(10, 6))

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=(24, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(header, image=self.logo_image).pack(side="left", padx=(0, 18))
        heading = ttk.Frame(header)
        heading.pack(side="left", fill="x", expand=True)
        ttk.Label(
            heading,
            text="UNIVERSITY OF GIBRALTAR",
            font=("Segoe UI", 11, "bold"),
            foreground="#a30022",
        ).pack(anchor="w", pady=(0, 3))
        ttk.Label(
            heading, text="Hamming Code Demonstrator", style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            heading,
            text=(
                "Encode 4 data bits, simulate a transmission error, and use the "
                "parity-check syndrome to locate it."
            ),
            style="Subtitle.TLabel",
            wraplength=760,
        ).pack(anchor="w", pady=(3, 0))

        message_frame = ttk.LabelFrame(
            container, text="1. Original message", style="Section.TLabelframe"
        )
        message_frame.pack(fill="x", pady=(0, 12))
        message_row = ttk.Frame(message_frame, style="Card.TFrame")
        message_row.pack(fill="x")
        ttk.Label(message_row, text="Data bits D4 D3 D2 D1:").pack(side="left")
        self.data_entry = ttk.Entry(
            message_row, textvariable=self.data_var, width=12, font=("Consolas", 12)
        )
        self.data_entry.pack(side="left", padx=(8, 12))
        ttk.Button(
            message_row, text="Encode message", command=self.encode_message
        ).pack(side="left")

        original_frame = ttk.LabelFrame(
            container, text="2. Original 7-bit codeword", style="Section.TLabelframe"
        )
        original_frame.pack(fill="x", pady=(0, 12))
        self.original_bits_frame = ttk.Frame(original_frame, style="Card.TFrame")
        self.original_bits_frame.pack(fill="x")

        received_frame = ttk.LabelFrame(
            container, text="3. Received message", style="Section.TLabelframe"
        )
        received_frame.pack(fill="x", pady=(0, 12))
        received_controls = ttk.Frame(received_frame, style="Card.TFrame")
        received_controls.pack(fill="x", pady=(0, 10))
        ttk.Label(received_controls, text="Received bits (editable):").pack(side="left")
        self.received_entry = ttk.Entry(
            received_controls,
            textvariable=self.received_var,
            width=12,
            font=("Consolas", 12),
        )
        self.received_entry.pack(side="left", padx=(8, 14))
        ttk.Label(received_controls, text="Flip bit position:").pack(side="left")
        self.position_box = ttk.Combobox(
            received_controls,
            textvariable=self.flip_position_var,
            values=tuple(str(position) for position in range(1, 8)),
            width=3,
            state="readonly",
        )
        self.position_box.pack(side="left", padx=(8, 8))
        ttk.Button(
            received_controls, text="Flip selected bit", command=self.flip_selected_bit
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            received_controls, text="Check received bits", command=self.check_message
        ).pack(side="left")
        self.received_bits_frame = ttk.Frame(received_frame, style="Card.TFrame")
        self.received_bits_frame.pack(fill="x")

        result_frame = ttk.LabelFrame(
            container, text="4. Receiver analysis", style="Section.TLabelframe"
        )
        result_frame.pack(fill="x")
        ttk.Label(
            result_frame,
            textvariable=self.result_var,
            font=("Segoe UI", 11, "bold"),
            wraplength=760,
        ).pack(anchor="w")
        ttk.Label(result_frame, textvariable=self.checks_var).pack(
            anchor="w", pady=(8, 0)
        )
        ttk.Label(result_frame, textvariable=self.corrected_var).pack(
            anchor="w", pady=(4, 0)
        )
        ttk.Label(result_frame, textvariable=self.recovered_var).pack(
            anchor="w", pady=(4, 0)
        )
        ttk.Label(
            container,
            text=(
                "Positions 1, 2, and 4 hold even-parity bits; data is at "
                "positions 3, 5, 6, and 7. Hamming(7, 4) locates and corrects "
                "a single-bit error; multiple flipped bits can be misidentified."
            ),
            style="Subtitle.TLabel",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(12, 0))

    def _render_bits(
        self, parent: ttk.Frame, codeword: str, highlighted_position: int | None = None
    ) -> None:
        for child in parent.winfo_children():
            child.destroy()
        for position, bit in enumerate(codeword, start=1):
            highlighted = position == highlighted_position
            background = "#fde2e2" if highlighted else "#edf2f8"
            foreground = "#a12626" if highlighted else "#17365d"
            card = tk.Frame(parent, bg=background, bd=1, relief="solid")
            card.grid(row=0, column=position - 1, padx=(0, 7), sticky="nsew")
            tk.Label(
                card,
                text=f"{position} · {BIT_LABELS[position]}",
                bg=background,
                fg=foreground,
                font=("Segoe UI", 9),
                padx=10,
                pady=5,
            ).pack()
            tk.Label(
                card,
                text=bit,
                bg=background,
                fg=foreground,
                font=("Consolas", 17, "bold"),
                padx=10,
                pady=2,
            ).pack()

    def encode_message(self) -> None:
        try:
            self.original_word = encode_hamming(self.data_var.get())
        except ValueError as error:
            messagebox.showerror("Invalid original message", str(error), parent=self.root)
            return
        self._render_bits(self.original_bits_frame, self.original_word)
        self.received_var.set(self.original_word)
        self._render_bits(self.received_bits_frame, self.original_word)
        self.result_var.set("Message encoded. Flip or edit a received bit, then check it.")
        self.checks_var.set("Parity checks: —")
        self.corrected_var.set("Corrected code: —")
        self.recovered_var.set("Recovered data: —")

    def flip_selected_bit(self) -> None:
        try:
            received = _validate_bits(self.received_var.get(), 7, "Received message")
            position = int(self.flip_position_var.get())
            changed = list(received)
            changed[position - 1] = "1" if changed[position - 1] == "0" else "0"
        except (ValueError, IndexError) as error:
            messagebox.showerror(
                "Cannot flip bit", str(error) or "Choose a position from 1 to 7.",
                parent=self.root,
            )
            return
        self.received_var.set("".join(changed))
        self._render_bits(self.received_bits_frame, self.received_var.get())
        self.result_var.set(f"Bit {position} flipped. Check the received bits to locate it.")
        self.checks_var.set("Parity checks: —")
        self.corrected_var.set("Corrected code: —")
        self.recovered_var.set("Recovered data: —")

    def check_message(self) -> None:
        try:
            received = _validate_bits(self.received_var.get(), 7, "Received message")
            error_position, checks = calculate_syndrome(received)
            corrected = correct_single_bit(received, error_position)
        except ValueError as error:
            messagebox.showerror("Invalid received message", str(error), parent=self.root)
            return

        self._render_bits(
            self.received_bits_frame, received, highlighted_position=error_position or None
        )
        check_summary = "  ".join(
            f"P{position}={'FAIL' if failed else 'OK'}"
            for position, failed in checks.items()
        )
        self.checks_var.set(f"Parity checks: {check_summary}    Syndrome: {error_position:03b}")
        self.corrected_var.set(f"Corrected code: {corrected}")
        self.recovered_var.set(f"Recovered data (D4 D3 D2 D1): {extract_data(corrected)}")
        if error_position:
            self.result_var.set(
                f"Single-bit error detected at position {error_position} "
                f"({BIT_LABELS[error_position]}). The highlighted bit is the one to flip."
            )
        else:
            self.result_var.set("No single-bit error detected: all parity checks pass.")


def main() -> None:
    root = tk.Tk()
    HammingDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
