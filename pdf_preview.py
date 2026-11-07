
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk


class PdfPreviewWindow(tk.Toplevel):
    def __init__(self, parent, pdf_document):
        super().__init__(parent)

        self.parent = parent
        self.pdf_document = pdf_document

        # Результат, который вернём главному окну
        self.result = None

        # Текущая отображаемая страница (индексация с нуля)
        self.current_page = 0

        self.title("Предварительный просмотр PDF")
        self.geometry("800x650")
        self.minsize(500, 400)

        # Делаем окно дочерним по отношению к главному
        self.transient(parent)

        # Блокируем взаимодействие с главным окном
        self.grab_set()

        # Обработка закрытия окна крестиком
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self._build_ui()

        self.page_count = self.pdf_document.page_count

        # Кортеж с номерами и количеством страниц
        self.page_selector["values"] = tuple(
            range(1, self.page_count + 1)
        )

        # Установка начального значения страницы на 1
        self.page_selector.set("1")
        self._update_navigation_buttons()

        # Сначала рассчитываем размеры и расположение элементов интерфейса.
        self.update_idletasks()
        self._display_page()

    def _build_ui(self):
        """Создаёт элементы интерфейса."""

        # Основная область окна
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Область будущего предпросмотра
        self.preview_frame = ttk.Frame(
            self.main_frame,
            relief="sunken",
            borderwidth=1
        )
        self.preview_frame.pack(fill="both", expand=True)

        self.preview_frame.bind(
            "<Configure>",
            self._on_preview_resize
        )

        self.preview_label = ttk.Label(
            self.preview_frame,
            text="Здесь пока ничего нет"
        )
        self.preview_label.pack(expand=True)

        # Область навигации
        self.navigation_frame = ttk.Frame(self.main_frame)
        self.navigation_frame.pack(pady=10)

        # Кнопка предыдущей страницы
        self.previous_button = ttk.Button(
            self.navigation_frame,
            text="Предыдущая",
            command=self._previous_page
        )
        self.previous_button.pack(side="left", padx=5)

        # Комбобокс с номерами страниц
        self.page_selector = ttk.Combobox(
            self.navigation_frame,
            state="normal",
            width=8,
            justify="center"
        )
        self.page_selector.pack(side="left", padx=5)

        self.page_selector.bind(
            "<<ComboboxSelected>>",
            self._on_page_selected
        )

        self.page_selector.bind(
            "<KeyRelease>",
            self._on_page_typed
        )

        # Кнопка следующей страницы
        self.next_button = ttk.Button(
            self.navigation_frame,
            text="Следующая",
            command=self._next_page
        )
        self.next_button.pack(side="left", padx=5)

        # Здесь позднее разместим кнопки импорта и отмены
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill="x")

        self.cancel_button = ttk.Button(
            self.buttons_frame,
            text="Отмена",
            command=self.cancel
        )
        self.cancel_button.pack(side="right", padx=5)

        self.import_button = ttk.Button(
            self.buttons_frame,
            text="Импортировать",
            command=self.import_page
        )
        self.import_button.pack(side="right", padx=5)

    def _on_preview_resize(self, event):
        """Обновляет масштаб страницы при изменении размера области."""

        if hasattr(self, "current_page_image"):
            self._update_preview_image()

    def _display_page(self):
        """Загружает текущую страницу PDF и подготавливает её к отображению."""

        self.current_page_image = self.pdf_document.render_page(
            self.current_page,
            dpi=120
        )

        self._update_preview_image()

    def _update_preview_image(self):
        """Масштабирует страницу и отображает её в окне."""

        # Получаем реальные размеры области предпросмотра
        frame_width = self.preview_frame.winfo_width()
        frame_height = self.preview_frame.winfo_height()

        # Если размеры ещё не определены, пока ничего не делаем
        if frame_width <= 1 or frame_height <= 1:
            return

        # Оставляем небольшие отступы от краёв
        max_width = frame_width - 30
        max_height = frame_height - 30

        # Создаём копию, чтобы не изменять исходное изображение
        preview_image = self.current_page_image.copy()

        # Уменьшаем изображение с сохранением пропорций
        preview_image.thumbnail(
            (max_width, max_height),
            Image.Resampling.LANCZOS
        )

        # Преобразуем Pillow Image в изображение для Tkinter
        self.preview_photo = ImageTk.PhotoImage(preview_image)

        # Передаём изображение в Label
        self.preview_label.configure(
            image=self.preview_photo,
            text=""
        )

    def _go_to_page(self, page_number):
        """Переключает предпросмотр на указанную страницу."""

        if not 1 <= page_number <= self.page_count:
            return

        self.current_page = page_number - 1

        self.page_selector.set(str(page_number))

        self._display_page()

        self._update_navigation_buttons()

    def _previous_page(self):
        self._go_to_page(self.current_page)

    def _next_page(self):
        self._go_to_page(self.current_page + 2)

    def _update_navigation_buttons(self):
        self.previous_button.configure(
            state="disabled" if self.current_page == 0 else "normal"
        )

        self.next_button.configure(
            state="disabled" if self.current_page == self.page_count - 1 else "normal"
        )

    def _on_page_selected(self, event=None):
        try:
            page_number = int(self.page_selector.get())
            self._go_to_page(page_number)
        except ValueError:
            return

    def _on_page_typed(self, event=None):
        value = self.page_selector.get()

        if not value.isdigit():
            return

        page_number = int(value)

        if 1 <= page_number <= self.page_count:
            self._go_to_page(page_number)

    def import_page(self):
        """Импортирует выбранную страницу PDF."""

        try:
            self.result = self.pdf_document.render_page(
                self.current_page,
                dpi=300
            )

            self.destroy()
        except Exception as exc:
            messagebox.showerror(
                "Ошибка импорта",
                str(exc),
                parent=self
            )

    def cancel(self):
        """Закрывает окно без импорта страницы."""
        self.result = None
        self.destroy()
