import base64
import hashlib
from pathlib import Path


def excel_to_txt(excel_path: str, txt_path: str) -> None:
    """Convert an Excel file to a lossless Base64 text file."""
    data = Path(excel_path).read_bytes()
    Path(txt_path).write_text(
        base64.b64encode(data).decode("ascii"),
        encoding="ascii",
    )


def txt_to_excel(txt_path: str, excel_path: str) -> None:
    """Restore the original Excel file from Base64 text."""
    encoded = Path(txt_path).read_text(encoding="ascii")
    data = base64.b64decode(encoded, validate=True)
    Path(excel_path).write_bytes(data)


def main() -> None:
    original = "original.xlsx"
    encoded = "workbook.txt"
    restored = "restored.xlsx"

    excel_to_txt(original, encoded)
    txt_to_excel(encoded, restored)

    original_hash = hashlib.sha256(Path(original).read_bytes()).hexdigest()
    restored_hash = hashlib.sha256(Path(restored).read_bytes()).hexdigest()

    assert original_hash == restored_hash, "Files are different!"

    print("SUCCESS: Restored Excel file is 100% identical.")


if __name__ == "__main__":
    main()
