
"""Разворот изображения."""

from PIL import Image


def rotate_image(img: Image.Image, angle: int = 90) -> Image.Image:
    """Возвращает развернутую копию изображения.

    Положительные углы отсчитываются против часовой стрелки.
    Поддерживаемые углы: 0, 90, 180, 270 градусов.
    """

    angle %= 360

    if angle not in (0, 90, 180, 270):
        raise ValueError("Не верный угол")

    if angle == 0:
        return img.copy()

    return img.rotate(angle, expand=True)
