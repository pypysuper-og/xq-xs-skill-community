"""Build a portable xq-xs ZIP from the distributable skill files only."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "xq-xs"
ROOT_FILES = {"SKILL.md", "LICENSE", "THIRD_PARTY_NOTICES.md"}
DIRECTORIES = {"agents", "assets", "data", "references", "scripts"}
EXTENSIONS = {".md", ".yaml", ".json", ".py", ".xs"}


def package_files(skill: Path) -> list[Path]:
    for name in ROOT_FILES:
        if not (skill / name).is_file():
            raise ValueError(f"Missing required skill file: {name}")
    files = []
    for path in sorted(skill.rglob("*")):
        relative = path.relative_to(skill)
        if "__pycache__" in relative.parts:
            continue
        if path.is_symlink():
            raise ValueError("Symlinks are not distributable skill resources")
        if not path.is_file():
            continue
        if len(relative.parts) == 1:
            if relative.name not in ROOT_FILES:
                raise ValueError(f"Unexpected skill root file: {relative.name}")
        elif relative.parts[0] not in DIRECTORIES or path.suffix not in EXTENSIONS:
            raise ValueError(f"Unexpected skill resource: {relative.as_posix()}")
        files.append(path)
    return files


def build_package(skill: Path, output: Path) -> tuple[str, int]:
    if output.resolve().is_relative_to(skill.resolve()):
        raise ValueError("The archive must be outside the source skill directory")
    files = package_files(skill)
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            name = (Path("xq-xs") / path.relative_to(skill)).as_posix()
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8", newline="\n")
    return digest, len(files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "xq-xs.zip")
    args = parser.parse_args()
    try:
        digest, count = build_package(SKILL, args.output)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Package build failed: {error}\n")
    print(f"Built {args.output.name}: {count} files; SHA-256 {digest}")


if __name__ == "__main__":
    main()
