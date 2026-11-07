
import unittest
from PIL import Image

from transformer import rotate_image


class TestRotateImage(unittest.TestCase):

    def setUp(self):
        self.img = Image.new("RGB", (100, 60), "red")

    def test_rotate_90(self):
        """Поворот на 90 градусов меняет ширину и высоту местами."""
        result = rotate_image(self.img, 90)

        self.assertEqual(result.size, (60, 100))

    def test_rotate_180(self):
        """Поворот на 180 градусов сохраняет размеры."""
        result = rotate_image(self.img, 180)

        self.assertEqual(result.size, (100, 60))

    def test_rotate_270(self):
        """Поворот на 270 градусов меняет ширину и высоту местами."""
        result = rotate_image(self.img, 270)

        self.assertEqual(result.size, (60, 100))

    def test_rotate_zero_returns_copy(self):
        """Нулевой поворот возвращает копию, а не исходное изображение."""
        result = rotate_image(self.img, 0)

        self.assertEqual(result.size, self.img.size)
        self.assertIsNot(result, self.img)

    def test_angle_normalization(self):
        """Углы за пределами диапазона нормализуются."""
        self.assertEqual(rotate_image(self.img, 450).size, (60, 100))
        self.assertEqual(rotate_image(self.img, -90).size, (60, 100))

    def test_invalid_angle_raises_error(self):
        """Угол, не кратный 90 градусам, вызывает ошибку."""
        with self.assertRaises(ValueError):
            rotate_image(self.img, 45)


if __name__ == "__main__":
    unittest.main()
