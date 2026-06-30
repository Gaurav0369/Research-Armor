from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("Workspace")

NOTES_DIR = Path(__file__).parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)


@mcp.tool
def save_note(filename: str, content: str) -> str:
    """
    Save a note to the workspace.
    """

    path = NOTES_DIR / filename

    path.write_text(content, encoding="utf-8")

    return f"Saved '{filename}' successfully."


@mcp.tool
def read_note(filename: str) -> str:
    path = NOTES_DIR / filename

    if not path.exists():
        return "Note not found."

    return path.read_text(encoding="utf-8")


@mcp.tool
def list_notes() -> list[str]:
    return [
        file.name
        for file in NOTES_DIR.iterdir()
        if file.is_file()
    ]

@mcp.tool
def delete_note(filename: str) -> str:
    path = NOTES_DIR / filename

    if not path.exists():
        return "Note not found."

    path.unlink()

    return f"Deleted '{filename}'."

@mcp.tool
def search_notes(query: str) -> list[str]:

    matches = []

    for file in NOTES_DIR.iterdir():

        if not file.is_file():
            continue

        text = file.read_text(encoding="utf-8")

        if query.lower() in text.lower():
            matches.append(file.name)

    return matches

if __name__ == "__main__":
    mcp.run()