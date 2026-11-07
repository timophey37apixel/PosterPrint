
import unittest

from layout import PageLayout
from page_geometry import calculate_page_geometry


class TestPageGeometry(unittest.TestCase):

    def setUp(self):
        self.layout = PageLayout(margin_mm=5)

    def test_fit_has_no_clip_rect(self):
        """В режиме fit обрезка не требуется."""
        result = calculate_page_geometry(
            2000, 1000, self.layout, mode="fit"
        )

        self.assertIsNone(result.clip_rect)

    def test_fit_preserves_aspect_ratio(self):
        """В режиме fit сохраняются пропорции изображения."""
        result = calculate_page_geometry(
            2000, 1000, self.layout, mode="fit"
        )

        _, _, width, height = result.image_rect
        self.assertAlmostEqual(width / height, 2.0)

    def test_fill_uses_printable_area_as_clip_rect(self):
        """В режиме fill обрезка ограничена областью печати."""
        result = calculate_page_geometry(
            2000, 1000, self.layout, mode="fill"
        )

        self.assertEqual(
            result.clip_rect,
            self.layout.get_printable_rect()
        )

    def test_fill_covers_printable_area(self):
        """В режиме fill изображение полностью покрывает область печати."""
        result = calculate_page_geometry(
            2000, 1000, self.layout, mode="fill"
        )

        x, y, width, height = result.image_rect
        px, py, pw, ph = result.printable_rect

        self.assertLessEqual(x, px)
        self.assertLessEqual(y, py)
        self.assertGreaterEqual(x + width, px + pw)
        self.assertGreaterEqual(y + height, py + ph)

    def test_stretch_matches_printable_area(self):
        """В режиме stretch изображение совпадает с областью печати."""
        result = calculate_page_geometry(
            2000, 1000, self.layout, mode="stretch"
        )

        self.assertEqual(
            result.image_rect,
            result.printable_rect
        )
        self.assertIsNone(result.clip_rect)

    def test_invalid_image_size_raises_error(self):
        """Нулевые и отрицательные размеры изображения запрещены."""
        with self.assertRaises(ValueError):
            calculate_page_geometry(0, 1000, self.layout)

        with self.assertRaises(ValueError):
            calculate_page_geometry(2000, -1000, self.layout)

    def test_invalid_mode_raises_error(self):
        """Неизвестный режим размещения вызывает ошибку."""
        with self.assertRaises(ValueError):
            calculate_page_geometry(
                2000, 1000, self.layout, mode="unknown"
            )


if __name__ == "__main__":
    unittest.main()
