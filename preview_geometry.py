"""Преобразует геометрию PDF-страницы PosterPrint в координаты для предварительного просмотра на экране.

Геометрия PDF использует точки с началом координат в левом нижнем углу.
Предварительный просмотр на экране использует пиксели с началом координат в левом верхнем углу.
Этот модуль не зависит от инструментария графического интерфейса пользователя,
поэтому PyQt6 или Tkinter могут использовать те же вычисления.
"""

from dataclasses import dataclass
from page_geometry import PageGeometry, calculate_page_geometry


@dataclass(frozen=True)
class PreviewGeometry:
    """Геометрия в пикселях предварительного просмотра, с началом координат в левом верхнем углу."""

    page_rect: tuple[float, float, float, float]
    printable_rect: tuple[float, float, float, float]
    image_rect: tuple[float, float, float, float]
    scale: float


def _pdf_rect_to_screen(rect, page_height: float, scale: float, offset_x: float, offset_y: float):
    x, y, width, height = rect
    return (
        offset_x + x * scale,
        offset_y + (page_height - y - height) * scale,
        width * scale,
        height * scale,
    )


def calculate_preview_geometry(
    image_width: float,
    image_height: float,
    layout,
    mode: str = "fit",
    *,
    preview_width: float = 420,
    preview_height: float = 594,
    padding: float = 12,
) -> PreviewGeometry:
    """Рассчитывает прямоугольники для страницы, области печати и изображения для предварительного просмотра на экране.

    Страница масштабируется равномерно так, чтобы поместиться в область предварительного просмотра с учетом отступов.
    Соотношение сторон сохраняется.
    Возвращаемые координаты задаются относительно верхнего левого угла виджета/холста предварительного просмотра.
    """
    if preview_width <= 0 or preview_height <= 0:
        raise ValueError("Размеры предварительного просмотра должны быть положительными")
    if padding < 0:
        raise ValueError("Отступ не может быть отрицательным")
    if preview_width <= 2 * padding or preview_height <= 2 * padding:
        raise ValueError("Область предварительного просмотра слишком мала для заданных отступов.")

    page_w = layout.page_width
    page_h = layout.page_height
    scale = min(
        (preview_width - 2 * padding) / page_w,
        (preview_height - 2 * padding) / page_h,
    )
    rendered_w = page_w * scale
    rendered_h = page_h * scale
    offset_x = (preview_width - rendered_w) / 2
    offset_y = (preview_height - rendered_h) / 2

    page_rect = (offset_x, offset_y, rendered_w, rendered_h)
    printable_rect = _pdf_rect_to_screen(
        layout.get_printable_rect(), page_h, scale, offset_x, offset_y
    )
    final = calculate_page_geometry(image_width, image_height, layout, mode)
    image_rect = _pdf_rect_to_screen(
        final.image_rect, page_h, scale, offset_x, offset_y
    )

    return PreviewGeometry(
        page_rect=page_rect,
        printable_rect=printable_rect,
        image_rect=image_rect,
        scale=scale,
    )
