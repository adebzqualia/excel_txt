
import base64
import hashlib
import json
from pathlib import Path


def split_txt(txt_path: str, output_dir: str, chunk_size: int = 50_000) -> None:
    """Split a Base64 text file into ordered chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    source = Path(txt_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    for old_chunk in output.glob("chunk_*.txt"):
        old_chunk.unlink()

    content = source.read_text(encoding="ascii")
    chunks = [
        content[i:i + chunk_size]
        for i in range(0, len(content), chunk_size)
    ]

    for i, chunk in enumerate(chunks, start=1):
        (output / f"chunk_{i:06d}.txt").write_text(
            chunk, encoding="ascii"
        )

    manifest = {
        "chunk_count": len(chunks),
        "sha256": hashlib.sha256(content.encode("ascii")).hexdigest(),
    }

    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(f"Created {len(chunks)} chunks in {output}")


def merge_txt(chunks_dir: str, output_txt: str) -> None:
    """Merge chunks and verify the original Base64 content."""
    directory = Path(chunks_dir)
    manifest = json.loads(
        (directory / "manifest.json").read_text(encoding="utf-8")
    )

    chunks = sorted(directory.glob("chunk_*.txt"))
    expected = [
        directory / f"chunk_{i:06d}.txt"
        for i in range(1, manifest["chunk_count"] + 1)
    ]

    if chunks != expected:
        raise ValueError("Missing or unexpected chunks.")

    content = "".join(
        chunk.read_text(encoding="ascii") for chunk in chunks
    )

    digest = hashlib.sha256(content.encode("ascii")).hexdigest()
    if digest != manifest["sha256"]:
        raise ValueError("Chunk integrity verification failed.")

    Path(output_txt).write_text(content, encoding="ascii")
    print("All chunks merged and verified successfully.")


def txt_to_excel(txt_path: str, excel_path: str) -> None:
    """Restore the exact Excel file from Base64 text."""
    encoded = Path(txt_path).read_text(encoding="ascii")
    data = base64.b64decode(encoded, validate=True)
    Path(excel_path).write_bytes(data)


def main() -> None:
    # Step 1: Split the existing Base64 text file
    split_txt("workbook.txt", "chunks", chunk_size=50_000)

    # Step 2: Reconstruct the original Base64 text file
    merge_txt("chunks", "reconstructed.txt")

    # Step 3: Reconstruct the original Excel workbook
    txt_to_excel("reconstructed.txt", "restored.xlsx")


if __name__ == "__main__":
    main()
