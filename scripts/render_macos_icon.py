from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def render_iconset(svg_path: Path, iconset_path: Path) -> None:
    app = QGuiApplication.instance() or QGuiApplication([])
    _ = app

    renderer = QSvgRenderer(str(svg_path))
    if not renderer.isValid():
        raise SystemExit(f"Invalid SVG: {svg_path}")

    iconset_path.mkdir(parents=True, exist_ok=True)
    for size in (16, 32, 128, 256, 512):
        for scale, suffix in ((1, ""), (2, "@2x")):
            pixels = size * scale
            image = QImage(pixels, pixels, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(Qt.GlobalColor.transparent)

            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            renderer.render(painter)
            painter.end()

            output = iconset_path / f"icon_{size}x{size}{suffix}.png"
            if not image.save(str(output)):
                raise SystemExit(f"Failed to write {output}")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: render_macos_icon.py ICON.svg OUTPUT.iconset")
    render_iconset(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
