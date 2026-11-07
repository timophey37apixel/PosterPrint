"""Вспомогательные средства для разделения изображений"""

from PIL import Image


def split_image(img: Image.Image, rows: int = 2, cols: int = 2) -> list[Image.Image]:
    """Основная функция разделения"""
    if not isinstance(rows, int) or not isinstance(cols, int):
        raise TypeError("Строки и столбцы должны быть целочисленными")
    if rows < 1 or cols < 1:
        raise ValueError("Строки и столбцы должны быть положительными")

    width, height = img.size
    if width < cols or height < rows:
        raise ValueError("Несоответствие размеров изображения и сетки")

    tiles = []
    for row in range(rows):
        top = row * height // rows
        bottom = (row + 1) * height // rows
        for col in range(cols):
            left = col * width // cols
            right = (col + 1) * width // cols
            tiles.append(img.crop((left, top, right, bottom)))
    return tiles


def simple_split_2x2(img: Image.Image) -> list[Image.Image]:
    """Старая версия для обратной совместимости"""
    width, height = img.size
    if width < 1 or height < 1:
        raise ValueError("Исходное изображение должно иметь ненулевые размеры.")
    enlarged = img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
    return split_image(enlarged, rows=2, cols=2)


def split_image_2x2(img: Image.Image) -> list[Image.Image]:
    """Старая версия для обратной совместимости"""
    return split_image(img, rows=2, cols=2)
