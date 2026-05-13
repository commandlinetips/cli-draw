# cli-draw

A small terminal drawing tool with mouse support.

## Install

Clone the repo:

```bash
git clone https://github.com/Kartik-2239/cli-draw.git
cd cli-draw
```

Install with `uv`:

```bash
uv sync
```

Run it:

```bash
uv run cli-draw
```

## Open Or Save A File

Open an existing drawing:

```bash
uv run cli-draw artwork.txt
```

Set the save path:

```bash
uv run cli-draw --save output.txt
```

Open a file and save back to another path:

```bash
uv run cli-draw artwork.txt --save output.txt
```

## Controls

- Left click: draw
- Left click + drag: draw continuously
- `0` to `7`: change color
- `b`: change brush character
- `c`: clear
- `u`: undo
- `s`: save
- `y`: copy ANSI-colored output to clipboard
- `q` or `Esc`: quit

## Notes

- Files saved by the app keep ANSI colors.
- If mouse drag does not work, use a terminal with mouse reporting enabled.
