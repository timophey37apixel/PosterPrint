"""
Общая геометрия страницы для экспорта и предварительного просмотра.
Все координаты и размеры указаны в пунктах PDF; точка (0, 0) соответствует нижнему левому углу страницы.
Размеры изображения заданы в пикселях; для расчета размещения используется только их соотношение сторон.
"""
from dataclasses import dataclass
from typing import Literal

PlacementMode = Literal["fit", "fill", "stretch"]


@dataclass(frozen=True)
class PageGeometry:
    """Полный набор геометрических данных, необходимых для отрисовки одного фрагмента на странице."""
    page_width: float
    page_height: float
    printable_rect: tuple[float, float, float, float]
    image_rect: tuple[float, float, float, float]
    clip_rect: tuple[float, float, float, float] | None


def calculate_page_geometry(image_width: float, image_height: float, layout,
                            mode: PlacementMode = "fit") -> PageGeometry:
    """Расчет окончательного размещения изображения и прямоугольника обрезки для одной страницы."""
    if image_width <= 0 or image_height <= 0:
        raise ValueError("Размер изображения должен быть положительным")
    if mode not in {"fit", "fill", "stretch"}:
        raise ValueError("Режим должен быть 'fit', 'fill', or 'stretch'")

    printable = layout.get_printable_rect()
    if mode == "fit":
        image_rect = layout.fit(image_width, image_height)
        clip_rect = None
    elif mode == "fill":
        image_rect = layout.fill(image_width, image_height)
        clip_rect = printable
    else:
        image_rect = layout.stretch(image_width, image_height)
        clip_rect = None

    return PageGeometry(layout.page_width, layout.page_height, printable,
                        image_rect, clip_rect)
