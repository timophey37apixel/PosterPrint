
import unittest
from PIL import Image

from splitter import (
    split_image,
    simple_split_2x2,
    split_image_2x2,
)


class TestSplitImage(unittest.TestCase):

    def test_split_2x2(self):
        """Изображение делится на четыре одинаковых фрагмента."""
        img = Image.new("RGB", (100, 80))

        tiles = split_image(img, rows=2, cols=2)

        self.assertEqual(len(tiles), 4)

        for tile in tiles:
            self.assertEqual(tile.size, (50, 40))

    def test_split_handles_remainder_pixels(self):
        """При нечётных размерах изображения ни один пиксель не теряется."""
        img = Image.new("RGB", (101, 82))

        tiles = split_image(img, rows=3, cols=4)

        expected_sizes = [
            (25, 27), (25, 27), (25, 27), (26, 27),
            (25, 27), (25, 27), (25, 27), (26, 27),
            (25, 28), (25, 28), (25, 28), (26, 28),
        ]

        self.assertEqual(len(tiles), 12)
        self.assertEqual(
            [tile.size for tile in tiles],
            expected_sizes
        )

        total_area = sum(
            tile.width * tile.height for tile in tiles
        )
        self.assertEqual(total_area, 101 * 82)

    def test_split_preserves_pixel_order(self):
        """Фрагменты располагаются слева направо, сверху вниз."""
        img = Image.new("RGB", (4, 2))

        for x in range(4):
            for y in range(2):
                img.putpixel((x, y), (x * 50, y * 100, 0))

        tiles = split_image(img, rows=2, cols=2)

        expected_first_pixel_colors = [
            (0, 0, 0),
            (100, 0, 0),
            (0, 100, 0),
            (100, 100, 0),
        ]

        actual_colors = [
            tile.getpixel((0, 0)) for tile in tiles
        ]

        self.assertEqual(actual_colors, expected_first_pixel_colors)

    def test_invalid_grid_type_raises_error(self):
        """Строки и столбцы должны быть целыми числами."""
        img = Image.new("RGB", (100, 100))

        with self.assertRaises(TypeError):
            split_image(img, rows=2.5, cols=2)

        with self.assertRaises(TypeError):
            split_image(img, rows=2, cols="2")

    def test_invalid_grid_size_raises_error(self):
        """Количество строк и столбцов должно быть положительным."""
        img = Image.new("RGB", (100, 100))

        with self.assertRaises(ValueError):
            split_image(img, rows=0, cols=2)

        with self.assertRaises(ValueError):
            split_image(img, rows=2, cols=-1)

    def test_image_smaller_than_grid_raises_error(self):
        """Нельзя разделить изображение на большее число частей, чем пикселей."""
        img = Image.new("RGB", (2, 2))

        with self.assertRaises(ValueError):
            split_image(img, rows=3, cols=2)

    def test_simple_split_2x2(self):
        """Старая функция увеличивает изображение и делит его на четыре части."""
        img = Image.new("RGB", (100, 80))

        tiles = simple_split_2x2(img)

        self.assertEqual(len(tiles), 4)

        for tile in tiles:
            self.assertEqual(tile.size, (100, 80))

    def test_split_image_2x2(self):
        """Старая функция корректно вызывает основное разделение."""
        img = Image.new("RGB", (100, 80))

        tiles = split_image_2x2(img)

        self.assertEqual(len(tiles), 4)

        for tile in tiles:
            self.assertEqual(tile.size, (50, 40))


if __name__ == "__main__":
    unittest.main()
