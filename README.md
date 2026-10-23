# University of Gibraltar Hamming Code Demonstrator

This small Python app helps you explore how a Hamming code can detect and
correct a bit that changes while a message is being transmitted. It uses a
graphical interface built with Tkinter and the Hamming **(7, 4)** code.

## The idea

Imagine sending a binary message across a noisy connection. A transmitted `0`
might arrive as `1`, or a `1` might arrive as `0`. The receiver has no direct
way to tell which bit changed just by looking at the message.

A Hamming code adds extra **parity bits** to the data. Each parity bit checks a
different group of positions. If a bit flips, the pattern of failed checks
forms a **syndrome**. For a single-bit error, the syndrome identifies the
position to correct.

Hamming (7, 4) takes **4 data bits** and encodes them into a **7-bit codeword**:
four bits carry the original data, and three bits provide parity checks.

## Bit positions and parity

This app displays the codeword from **position 1 on the left** to **position 7
on the right**. The parity bits occupy positions that are powers of two:

| Position | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Role | P1 | P2 | D1 | P4 | D2 | D3 | D4 |

The original data is entered and recovered in the order **D4 D3 D2 D1**.
The parity is **even**: each group must contain an even number of `1` bits.

| Check | Positions checked |
| --- | --- |
| P1 | 1, 3, 5, 7 |
| P2 | 2, 3, 6, 7 |
| P4 | 4, 5, 6, 7 |

The parity bit is included in its own check. For example, P1 is chosen so that
the bits at positions 1, 3, 5, and 7 have even parity. In binary arithmetic,
calculating even parity is the same as XOR-ing the bits in the group.

## Worked example

Start with the data `1011` (`D4=1`, `D3=0`, `D2=1`, `D1=1`) and place the data
bits in their positions:

```text
Position: 1 2 3 4 5 6 7
Role:     P1 P2 D1 P4 D2 D3 D4
Value:    _  _  1  _  1  0  1
```

Choose the parity bits to make each check even:

- **P1** checks positions 1, 3, 5, 7. Since the data bits are `1, 1, 1`,
  set P1 to `1`; the group has four `1`s.
- **P2** checks positions 2, 3, 6, 7. The data bits are `1, 0, 1`, so set P2
  to `0`; the group already has two `1`s.
- **P4** checks positions 4, 5, 6, 7. The data bits are `1, 0, 1`, so set P4
  to `0`; this group also has two `1`s.

The complete codeword is **`1010101`**. Suppose position 5 flips during
transmission. The receiver gets **`1010001`**:

| Parity check | Result |
| --- | --- |
| P1 (positions 1, 3, 5, 7) | Fails |
| P2 (positions 2, 3, 6, 7) | Passes |
| P4 (positions 4, 5, 6, 7) | Fails |

Write the results as a binary number in the order **P4 P2 P1**:

```text
P4 P2 P1 = 1 0 1 = 101₂ = 5
```

The syndrome points to **position 5**. Flip that received bit back to recover
`1010101`, then read data positions 7, 6, 5, 3 to recover the original message
`1011`.

## Download or build for Windows

A standalone Windows executable has been built at
[`dist/HammingCodeDemo.exe`](./dist/HammingCodeDemo.exe). It bundles Python,
Tkinter, and the University of Gibraltar logo, so a student does not need to
install Python to run it. Download the `.exe` and double-click it.

To build your own copy, use Windows with Python installed, open PowerShell in
the project folder, and run:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed `
  --name HammingCodeDemo --add-data "logo.png;." hamming_demo.py
```

The executable will be created as `dist\HammingCodeDemo.exe`. The
`--add-data "logo.png;."` option embeds the logo, and `--onefile` makes a single
file to share. Build on Windows to produce a Windows executable; PyInstaller
does not cross-compile executables for other operating systems. The first
launch of a one-file build may take a few seconds while it unpacks its bundled
files.

For sharing with a class, upload the executable to a trusted course page or a
GitHub Release. Windows may show a SmartScreen warning for an unsigned
executable; students should only run it if they trust where it came from.
Code-signing with a trusted certificate can reduce those warnings for
published distributions.

## Run the app

You need Python 3 with Tkinter available. Tkinter is included with many Python
installations; on some systems it may need to be installed separately.

Keep `hamming_demo.py` and `logo.png` in the same folder, open a terminal in
that folder, and run:

```bash
python hamming_demo.py
```

## Play the browser game

Open [`hamming-game.html`](./hamming-game.html) in a browser to practise Hamming
codes. Standard mode asks you to locate a single flipped bit. Extended Hamming
(SECDED) mode adds an overall-parity bit and asks you to distinguish a
correctable single-bit error from a detectable, but not correctable, double-bit
error. Choose a Hamming code length from 3 to 31 bits; extended mode adds one
more bit to that codeword. A formula helper updates the data/parity counts for
the selected length. Easy mode marks parity positions; Hard mode hides those
hints until after an answer. The game has no build step or external
dependencies. A “How to find the bit” dialog provides the parity-check steps and
worked examples, including the SECDED syndrome/overall-parity cases. The repository includes
an Amplify build specification, and the root page redirects to the game. To
publish with AWS Amplify, push the game files to a GitHub branch, create an
Amplify Hosting app connected to that repository and branch, and let Amplify
use `amplify.yml`.
The spec publishes only `index.html`, `hamming-game.html`, and `logo.png`.
Keep the game HTML and logo together on other static hosts as well.

## Try it yourself

1. Enter four bits in **D4 D3 D2 D1** order, such as `1011`, and select
   **Encode message**.
2. Compare the original 7-bit codeword with the received message.
3. Choose a position from 1 to 7 and select **Flip selected bit**, or edit the
   received bits directly.
4. Select **Check received bits**. Observe which parity checks fail, the
   syndrome, the highlighted position, and the corrected codeword.
5. Try a different bit position or a different original message. Also try an
   unchanged codeword; all checks should pass and the syndrome should be zero.

## What the code can and cannot do

Hamming (7, 4) can **correct one flipped bit** in a codeword. With two or more
flipped bits, the syndrome does not reliably identify a single bad position;
the app's correction display assumes at most one error. A zero syndrome means
the checks pass, not that every possible multi-bit corruption has been ruled
out. Extended Hamming codes add another parity bit to improve detection of
multiple-bit errors.

## Project files

- `hamming_demo.py` — Tkinter interface and Hamming (7, 4) implementation.
- `hamming-game.html` — static browser game for locating a flipped bit; uses
  `logo.png` for University of Gibraltar branding.
- `logo.png` — University of Gibraltar logo displayed in the app.
- `test_hamming_demo.py` — unit tests for encoding, parity checks, and
  single-bit correction.
