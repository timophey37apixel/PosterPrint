"""Экспорт разделенного изображения в PDF файл, с использованием общей геометрии страниц."""
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from page_geometry import calculate_page_geometry

SUPPORTED_MODES = {"fit", "fill", "stretch"}


def export_tiles_to_pdf(tiles, layout, output_path="output.pdf", mode="fit"):
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Режим должен быть одним из: {', '.join(sorted(SUPPORTED_MODES))}")
    tiles = list(tiles)
    if not tiles:
        raise ValueError("Для экспорта требуется как минимум один фрагмент")

    pdf = canvas.Canvas(output_path, pagesize=(layout.page_width, layout.page_height))
    for tile in tiles:
        if tile.width <= 0 or tile.height <= 0:
            raise ValueError("Изображения фрагментов должны иметь ненулевые размеры")
        geometry = calculate_page_geometry(tile.width, tile.height, layout, mode)
        x, y, draw_w, draw_h = geometry.image_rect

        pdf.saveState()
        if geometry.clip_rect is not None:
            clip_x, clip_y, clip_w, clip_h = geometry.clip_rect
            clip_path = pdf.beginPath()
            clip_path.rect(clip_x, clip_y, clip_w, clip_h)
            pdf.clipPath(clip_path, stroke=0, fill=0)
        pdf.drawImage(ImageReader(tile), x, y, width=draw_w, height=draw_h)
        pdf.restoreState()
        pdf.showPage()
    pdf.save()
