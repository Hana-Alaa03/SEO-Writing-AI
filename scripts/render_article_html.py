"""Render article_final.md (or any markdown file) to styled page.html."""

import argparse
import re
from pathlib import Path

from src.utils.html_renderer import render_html_page


def _title_from_markdown(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled Article"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render markdown article to styled HTML")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="output",
        help="Folder containing article_final.md",
    )
    parser.add_argument(
        "--input",
        default="article_final.md",
        help="Markdown filename inside output_dir (default: article_final.md)",
    )
    parser.add_argument(
        "--output",
        default="page.html",
        help="HTML filename to write (default: page.html)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    md_path = output_dir / args.input
    if not md_path.exists():
        raise SystemExit(f"Markdown file not found: {md_path}")

    md_content = md_path.read_text(encoding="utf-8")
    title = _title_from_markdown(md_content)

    render_data = {
        "output_dir": str(output_dir),
        "final_markdown": md_content,
        "title": title,
        "meta_title": title,
        "meta_description": re.sub(r"\s+", " ", title)[:160],
        "meta_keywords": "",
        "article_language": "ar",
    }

    html_path = render_html_page(render_data)
    if not html_path:
        raise SystemExit("HTML rendering failed")

    target = output_dir / args.output
    if Path(html_path).name != args.output:
        Path(html_path).replace(target)

    print("HTML saved:", str(target))


if __name__ == "__main__":
    main()
