
import unittest

from layout import PageLayout
from preview_geometry import (
    calculate_preview_geometry,
    _pdf_rect_to_screen,
)


class TestPreviewGeometry(unittest.TestCase):

    def setUp(self):
        self.layout = PageLayout(margin_mm=5)

    def test_page_fits_inside_preview(self):
        """Страница целиком помещается в область предпросмотра."""
        result = calculate_preview_geometry(
            2000, 1000, self.layout
        )

        x, y, width, height = result.page_rect

        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)
        self.assertLessEqual(x + width, 420)
        self.assertLessEqual(y + height, 594)

    def test_page_preserves_aspect_ratio(self):
        """Масштабирование не изменяет пропорции страницы."""
        result = calculate_preview_geometry(
            2000, 1000, self.layout
        )

        _, _, width, height = result.page_rect

        self.assertAlmostEqual(
            width / height,
            self.layout.page_width / self.layout.page_height
        )

    def test_page_is_centered(self):
        """Страница располагается по центру холста."""
        result = calculate_preview_geometry(
            2000, 1000, self.layout
        )

        x, y, width, height = result.page_rect

        self.assertAlmostEqual(x + width / 2, 420 / 2)
        self.assertAlmostEqual(y + height / 2, 594 / 2)

    def test_scale_is_positive(self):
        """Масштаб предпросмотра должен быть положительным."""
        result = calculate_preview_geometry(
            2000, 1000, self.layout
        )

        self.assertGreater(result.scale, 0)

    def test_pdf_coordinates_are_converted_correctly(self):
        """Преобразование меняет направление вертикальной оси."""
        result = _pdf_rect_to_screen(
            (10, 20, 100, 50),
            page_height=800,
            scale=0.5,
            offset_x=5,
            offset_y=10,
        )

        self.assertEqual(result, (10, 375, 50, 25))

    def test_printable_area_is_inside_page(self):
        """Печатная область находится внутри страницы."""
        result = calculate_preview_geometry(
            2000, 1000, self.layout
        )

        px, py, pw, ph = result.page_rect
        x, y, width, height = result.printable_rect

        self.assertGreaterEqual(x, px)
        self.assertGreaterEqual(y, py)
        self.assertLessEqual(x + width, px + pw)
        self.assertLessEqual(y + height, py + ph)

    def test_invalid_preview_dimensions_raise_error(self):
        """Нулевые и отрицательные размеры предпросмотра запрещены."""
        with self.assertRaises(ValueError):
            calculate_preview_geometry(
                2000, 1000, self.layout, preview_width=0
            )

        with self.assertRaises(ValueError):
            calculate_preview_geometry(
                2000, 1000, self.layout, preview_height=-10
            )

    def test_invalid_padding_raises_error(self):
        """Отрицательные отступы запрещены."""
        with self.assertRaises(ValueError):
            calculate_preview_geometry(
                2000, 1000, self.layout, padding=-1
            )

    def test_padding_cannot_exceed_preview_area(self):
        """Отступы не должны занимать всю область предпросмотра."""
        with self.assertRaises(ValueError):
            calculate_preview_geometry(
                2000, 1000, self.layout, padding=300
            )


if __name__ == "__main__":
    unittest.main()
