

from pathlib import Path

from PIL import Image


class PdfDocument:
    """
    Открывает PDF документ. Создает предварительный просмотр всего файла.
    Конвертирует выбранную страницу в изображение.
    """

    def __init__(self, file_path):
        self.file_path = Path(file_path)

        try:
            import pymupdf  # PyMuPDF
        except ImportError as exc:
            raise ImportError(
                "Для импорта PDF установите PyMuPDF: python -m pip install pymupdf"
            ) from exc

        self._pymupdf = pymupdf

        try:
            self._document = self._pymupdf.open(str(self.file_path))
        except Exception as exc:
            raise ValueError(f"Не удалось открыть PDF-файл: {exc}") from exc

        if self._document.is_closed:
            raise ValueError("PDF-документ не удалось открыть.")

        if self._document.needs_pass:
            self._document.close()
            raise ValueError("PDF защищён паролем. Защищённые документы пока не поддерживаются.")

        if len(self._document) == 0:
            self._document.close()
            raise ValueError("PDF-документ не содержит страниц.")

    @property
    def page_count(self):            # Возвращает номер страницы документа
        return len(self._document)

    def render_page(self, page_index, dpi=180):  # Отрисовывает одну страницу в предварительном просмотре и возвращает изображение Pillow
        if not isinstance(page_index, int):
            raise TypeError("Номер страницы должен быть целым числом.")

        if not 0 <= page_index < self.page_count:
            raise IndexError(
                f"Страница {page_index + 1} вне диапазона 1–{self.page_count}."
            )

        if dpi <= 0:
            raise ValueError("Разрешение должно быть больше нуля.")

        page = self._document.load_page(page_index)
        scale = dpi / 72
        matrix = self._pymupdf.Matrix(scale, scale)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

        image = Image.frombytes(
            "RGB",
            (pixmap.width, pixmap.height),
            pixmap.samples,
        )
        return image

    # Закрывает PDF файл
    def close(self):
        if self._document is not None and not self._document.is_closed:
            self._document.close()
