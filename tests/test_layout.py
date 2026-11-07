
import unittest

from layout import PageLayout


class TestPageLayout(unittest.TestCase):

    def setUp(self):
        """Создаём стандартный лист A4 с полями 5 мм перед каждым тестом."""
        self.layout = PageLayout(margin_mm=5)

    def test_fit_stays_inside_printable_area(self):
        """Изображение после fit целиком помещается в область печати."""
        x, y, width, height = self.layout.fit(2000, 1000)

        px, py, pw, ph = self.layout.get_printable_rect()

        self.assertGreaterEqual(x, px)
        self.assertGreaterEqual(y, py)
        self.assertLessEqual(x + width, px + pw)
        self.assertLessEqual(y + height, py + ph)

    def test_fit_preserves_aspect_ratio(self):
        """Fit сохраняет исходные пропорции изображения."""
        _, _, width, height = self.layout.fit(2000, 1000)

        self.assertAlmostEqual(width / height, 2.0)

    def test_fill_covers_printable_area(self):
        """Fill полностью покрывает печатаемую область."""
        x, y, width, height = self.layout.fill(2000, 1000)

        px, py, pw, ph = self.layout.get_printable_rect()

        self.assertLessEqual(x, px)
        self.assertLessEqual(y, py)
        self.assertGreaterEqual(x + width, px + pw)
        self.assertGreaterEqual(y + height, py + ph)

    def test_fill_preserves_aspect_ratio(self):
        """Fill сохраняет исходные пропорции изображения."""
        _, _, width, height = self.layout.fill(2000, 1000)

        self.assertAlmostEqual(width / height, 2.0)

    def test_stretch_matches_printable_area(self):
        """Stretch точно совпадает с печатаемой областью."""
        result = self.layout.stretch(2000, 1000)
        expected = self.layout.get_printable_rect()

        self.assertEqual(result, expected)

    def test_invalid_image_size_raises_error(self):
        """Нулевые и отрицательные размеры изображения запрещены."""
        with self.assertRaises(ValueError):
            self.layout.fit(0, 1000)

        with self.assertRaises(ValueError):
            self.layout.fill(2000, -1000)


if __name__ == "__main__":
    unittest.main()
