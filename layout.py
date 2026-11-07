"""Расчёты геометрии и размещения страниц"""

from reportlab.lib.pagesizes import A4


def mm_to_pt(mm: float) -> float:
    """Конвертирование миллиметров в координаты PDF."""
    return mm * 72 / 25.4


class PageLayout:
    """
    Расчеты области печати на странице и размещения изображения.
    Отступы измеряются в миллиметрах.
    """

    def __init__(
        self,
        margin_mm: float = 5,
        page_size=A4,
        dpi: int = 300,
        *,
        left_margin_mm: float | None = None,
        right_margin_mm: float | None = None,
        top_margin_mm: float | None = None,
        bottom_margin_mm: float | None = None,
    ):
        self.page_width, self.page_height = page_size
        self.dpi = dpi
        # Keep the original public attribute for compatibility with older code.
        self.margin = mm_to_pt(margin_mm)

        self.left_margin = mm_to_pt(margin_mm if left_margin_mm is None else left_margin_mm)
        self.right_margin = mm_to_pt(margin_mm if right_margin_mm is None else right_margin_mm)
        self.top_margin = mm_to_pt(margin_mm if top_margin_mm is None else top_margin_mm)
        self.bottom_margin = mm_to_pt(margin_mm if bottom_margin_mm is None else bottom_margin_mm)

        margins = (self.left_margin, self.right_margin, self.top_margin, self.bottom_margin)
        if any(m < 0 for m in margins):
            raise ValueError("Поля не могут быть отрицательными")
        if self.printable_width <= 0 or self.printable_height <= 0:
            raise ValueError("Поля выходят за область")
        if self.page_width <= 0 or self.page_height <= 0:
            raise ValueError("размеры страницы должны быть положительными")
        if dpi <= 0:
            raise ValueError("dpi должен быть положительным")

    @property
    def printable_width(self) -> float:
        return self.page_width - self.left_margin - self.right_margin

    @property
    def printable_height(self) -> float:
        return self.page_height - self.top_margin - self.bottom_margin

    def get_origin(self) -> tuple[float, float]:
        """Возвращает координаты левого нижнего угла области печати в координатах PDF."""
        return self.left_margin, self.bottom_margin

    def get_printable_rect(self) -> tuple[float, float, float, float]:
        """Возвращает (x, y, ширина(width), высота(height)) печатаемой области."""
        return self.left_margin, self.bottom_margin, self.printable_width, self.printable_height

    @staticmethod
    def _validate_image_size(w: float, h: float) -> None:
        if w <= 0 or h <= 0:
            raise ValueError("размеры изображения должны быть положительными")

    def fit(self, w: float, h: float) -> tuple[float, float, float, float]:
        """Размещает всё изображение в области печати, сохранив соотношение сторон."""
        self._validate_image_size(w, h)
        scale = min(self.printable_width / w, self.printable_height / h)
        return self._apply_scale(w, h, scale)

    def fill(self, w: float, h: float) -> tuple[float, float, float, float]:
        """
        Заполняет область печати, сохраняя соотношение сторон.
        Полученное изображение может выходить за пределы прямоугольной области печати.
        Экспортер PDF обрезает его по границам этого прямоугольника, чтобы изображение не заходило на поля.
        """
        self._validate_image_size(w, h)
        scale = max(self.printable_width / w, self.printable_height / h)
        new_w = w * scale
        new_h = h * scale
        x = self.left_margin + (self.printable_width - new_w) / 2
        y = self.bottom_margin + (self.printable_height - new_h) / 2
        return x, y, new_w, new_h

    def stretch(self, w: float, h: float) -> tuple[float, float, float, float]:
        """Растягивает изображение на всю область печати, допуская искажения."""
        self._validate_image_size(w, h)
        return self.left_margin, self.bottom_margin, self.printable_width, self.printable_height

    def _apply_scale(self, w: float, h: float, scale: float) -> tuple[float, float, float, float]:
        new_w = w * scale
        new_h = h * scale
        x = self.left_margin + (self.printable_width - new_w) / 2
        y = self.bottom_margin + (self.printable_height - new_h) / 2
        return x, y, new_w, new_h
