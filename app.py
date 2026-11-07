"""Основное окно приложения.

app.py является стартовой точкой запуска приложения. Отвечает за создание функционального окна.
Объединяет большинство файлов, посредством вызова соответствующих функций настроек, импорта, экспорта,
предварительного просмотра.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import tempfile

from PIL import Image, ImageDraw, ImageTk

from layout import PageLayout
from preview_geometry import calculate_preview_geometry
from splitter import split_image
from transformer import rotate_image
from export import export_tiles_to_pdf


APP_TITLE = "PosterPrint"


class PosterPrintApp:
    GRID_OPTIONS = {
        "2 × 2 (4 страницы)": (2, 2),
        "3 × 3 (9 страниц)": (3, 3),
        "4 × 4 (16 страниц)": (4, 4),
    }

    MODE_LABELS = {
        "Вписать (fit)": "fit",
        "Заполнить с обрезкой (fill)": "fill",
        "Растянуть (stretch)": "stretch",
    }

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1100x790")
        self.root.minsize(900, 650)

        self.source_image = None
        self.source_path = None
        self.tiles = []
        self.current_page = 0
        self._preview_photo = None
        self.rotation_angle = 0

        self.mode_var = tk.StringVar(value="Вписать (fit)")
        self.grid_var = tk.StringVar(value="2 × 2 (4 страницы)")
        self.link_margins_var = tk.BooleanVar(value=True)
        self.margin_vars = {
            "left": tk.StringVar(value="5.0"),
            "right": tk.StringVar(value="5.0"),
            "top": tk.StringVar(value="5.0"),
            "bottom": tk.StringVar(value="5.0"),
        }
        self.page_label_var = tk.StringVar(value="Страница — из —")
        self.status_var = tk.StringVar(value="Выберите файл, чтобы начать.")

        self._build_ui()
        self._redraw_preview()

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(toolbar, text="Открыть файл…", command=self._open_image).pack(side="left")
        self.file_label = ttk.Label(toolbar, text="Файл не выбран", anchor="w")
        self.file_label.pack(side="left", padx=10, fill="x", expand=True)

        footer = ttk.Frame(toolbar)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Label(footer, textvariable=self.status_var).pack(side="right", fill="x", expand=True)

        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True)

        controls = ttk.LabelFrame(body, text="Настройки", padding=10)
        controls.pack(side="left", fill="y", padx=(0, 12))

        ttk.Label(controls, text="Сетка страниц").pack(anchor="w")
        grid_combo = ttk.Combobox(
            controls, textvariable=self.grid_var, state="readonly",
            values=tuple(self.GRID_OPTIONS), width=24
        )
        grid_combo.pack(fill="x", pady=(4, 12))
        grid_combo.bind("<<ComboboxSelected>>", self._on_grid_changed)

        ttk.Label(controls, text="Режим размещения").pack(anchor="w")
        mode_combo = ttk.Combobox(
            controls, textvariable=self.mode_var, state="readonly",
            values=tuple(self.MODE_LABELS), width=24
        )
        mode_combo.pack(fill="x", pady=(4, 12))
        mode_combo.bind("<<ComboboxSelected>>", lambda _event: self._redraw_preview())

        ttk.Label(controls, text="Поля листа (мм)").pack(anchor="w")
        ttk.Checkbutton(
            controls, text="Одинаковые со всех сторон",
            variable=self.link_margins_var, command=self._on_link_margins
        ).pack(anchor="w", pady=(3, 6))

        self.margin_widgets = {}
        for key, label in (
            ("left", "Слева"),
            ("right", "Справа"),
            ("top", "Сверху"),
            ("bottom", "Снизу"),
        ):
            row = ttk.Frame(controls)
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=label, width=9).pack(side="left")
            spin = ttk.Spinbox(
                row, from_=0, to=100, increment=0.1, width=8,
                textvariable=self.margin_vars[key], command=self._redraw_preview
            )
            spin.pack(side="right")
            spin.bind("<KeyRelease>", lambda _event: self._redraw_preview())
            spin.bind("<FocusOut>", lambda _event: self._redraw_preview())
            self.margin_widgets[key] = spin

        #-----------------------------------------------------------------------------------
        ttk.Separator(controls).pack(fill="x", pady=12)

        action_row = ttk.Frame(controls)
        action_row.pack(fill="x", pady=3)

        ttk.Label(action_row, text="Выбор страницы").pack(anchor="w", pady = (5,10))
        ttk.Label(action_row, textvariable=self.page_label_var, anchor="center").pack(
            side="bottom", fill="x", expand=True, padx=8, pady=5
        )
        self.prev_button = (ttk.Button(action_row, text="Предыдущая", command=self._previous_page))
        self.prev_button.pack(side="left")

        self.next_button = ttk.Button(action_row, text="Следующая ", command=self._next_page)
        self.next_button.pack(side="right")

        rotate_row = ttk.Frame(controls)
        rotate_row.pack(fill="x", pady=(0, 10))

        button_size = 50

        ttk.Label(rotate_row, text="Повернуть изображение").pack(anchor="w", pady = (10, 6))
        r_button = tk.Canvas(rotate_row, width=button_size, height=button_size, highlightthickness=0, cursor="hand2")
        r_button.create_rectangle(1, 1, button_size - 1, button_size - 1, fill="#eeeeee", outline="#888888", width=1)
        r_button.create_text(button_size / 2, button_size / 2, text="↻", font=("Arial", 24))
        r_button.pack(side="left", padx = (40, 0))
        r_button.bind("<Button-1>", lambda event: self._rotate_right())

        l_button = tk.Canvas(rotate_row, width=button_size, height=button_size, highlightthickness=0, cursor="hand2")
        l_button.create_rectangle(1, 1, button_size - 1, button_size - 1, fill="#eeeeee", outline="#888888", width=1)
        l_button.create_text(button_size / 2, button_size / 2, text="↺", font=("Arial", 24))
        l_button.pack(side="right", padx = (0, 40))
        l_button.bind("<Button-1>", lambda event: self._rotate_left())

        ttk.Separator(controls).pack(fill="x", pady=12)
        ttk.Label(
            controls,
            text="Формат листа: A4, книжная ориентация.\nКрасная рамка — печатная область.",
            justify="left", wraplength=220
        ).pack(anchor="w")
        ttk.Separator(controls).pack(fill="x", pady=12)

        export_row = ttk.Frame(controls)
        export_row.pack(fill="x", pady=(0, 10))

        ttk.Button(export_row, text="Экспорт", command=self._export_pdf).pack(side="right", pady=(4, 12))

        #---------------------------------------------------------------------------------------------

        preview_panel = ttk.LabelFrame(body, text="Предварительный просмотр страницы", padding=8)
        preview_panel.pack(side="left", fill="both", expand=True)
        self.preview_label = ttk.Label(preview_panel, anchor="center")
        self.preview_label.pack(fill="both", expand=True)


    def _on_link_margins(self):
        if self.link_margins_var.get():
            value = self.margin_vars["left"].get()
            for key in self.margin_vars:
                self.margin_vars[key].set(value)
        self._redraw_preview()

    def _read_margins(self):
        values = {}
        for key, var in self.margin_vars.items():
            raw = var.get().strip().replace(",", ".")
            value = float(raw)
            if value < 0:
                raise ValueError("Поля не могут быть отрицательными.")
            values[key] = value
        if self.link_margins_var.get():
            master = values["left"]
            values = {key: master for key in values}
        return values

    def _make_layout(self):
        m = self._read_margins()
        return PageLayout(
            left_margin_mm=m["left"],
            right_margin_mm=m["right"],
            top_margin_mm=m["top"],
            bottom_margin_mm=m["bottom"],
        )

    def _current_mode(self):
        return self.MODE_LABELS[self.mode_var.get()]

    def _get_effective_grid(self):
        rows, cols = self.GRID_OPTIONS[self.grid_var.get()]

        # При повороте на 90° или 270° меняем
        # количество строк и столбцов местами.
        if self.rotation_angle % 180 != 0:
            rows, cols = cols, rows

        return rows, cols

    def _rebuild_tiles(self, reset_page=True):
        self.tiles = []

        if reset_page:
            self.current_page = 0

        if self.source_image is not None:
            rows, cols = self._get_effective_grid()

            rotated_image = rotate_image(
                self.source_image,
                self.rotation_angle
            )

            self.tiles = split_image(
                rotated_image,
                rows=rows,
                cols=cols
            )

            # Защита от выхода за границы списка страниц.
            if self.tiles:
                self.current_page = min(
                    self.current_page,
                    len(self.tiles) - 1
                )
            else:
                self.current_page = 0

    def _on_grid_changed(self, _event=None):
        try:
            self._rebuild_tiles()
            self._redraw_preview()
        except Exception as exc:
            messagebox.showerror("Не удалось разделить изображение", str(exc), parent=self.root)

    def _open_image(self):
        path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[
                ("Поддерживаемые файлы",
                 "*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff *.pdf *.docx"),
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff"),
                ("PDF-файлы", "*.pdf"),
                ("Документы Word", "*.docx"),
                ("Все файлы", "*.*"),
            ],
        )

        if not path:
            return

        try:

            extension = Path(path).suffix.lower()

            if extension in (".pdf", ".docx"):

                # Если выбран DOCX, сначала преобразуем его в PDF.
                if extension == ".docx":
                    from docx_importer import convert_docx_to_pdf

                    # Временная папка будет существовать,
                    # пока открыто окно предварительного просмотра.
                    with tempfile.TemporaryDirectory() as temp_dir:
                        pdf_path = Path(temp_dir) / "converted.pdf"

                        convert_docx_to_pdf(path, pdf_path)

                        from pdf_importer import PdfDocument
                        from pdf_preview import PdfPreviewWindow

                        pdf_document = PdfDocument(pdf_path)

                        try:
                            preview = PdfPreviewWindow(self.root, pdf_document)
                            self.root.wait_window(preview)
                            img = preview.result
                        finally:
                            pdf_document.close()

                else:
                    from pdf_importer import PdfDocument
                    from pdf_preview import PdfPreviewWindow

                    pdf_document = PdfDocument(path)

                    try:
                        preview = PdfPreviewWindow(self.root, pdf_document)
                        self.root.wait_window(preview)
                        img = preview.result
                    finally:
                        pdf_document.close()

                if img is None:
                    return

            else:
                with Image.open(path) as img_file:
                    img = img_file.convert("RGB")

            self.source_image = img.convert("RGB")
            self.source_path = path
            self.rotation_angle = 0
            self.file_label.configure(text=Path(path).name)

            self._rebuild_tiles()
            self._redraw_preview()

        except Exception as exc:
            messagebox.showerror(
                "Не удалось открыть файл",
                str(exc),
                parent=self.root
            )

    def _previous_page(self):
        if self.tiles and self.current_page > 0:
            self.current_page -= 1
            self._redraw_preview()

    def _next_page(self):
        if self.tiles and self.current_page < len(self.tiles) - 1:
            self.current_page += 1
            self._redraw_preview()

    def _rotate_image_by(self, delta):
        if self.source_image is None:
            return

        # Запоминаем координаты текущего фрагмента.
        old_rows, old_cols = self._get_effective_grid()

        old_page = min(
            self.current_page,
            old_rows * old_cols - 1
        )

        old_row, old_col = divmod(old_page, old_cols)

        if delta == 90:
            # Поворот против часовой стрелки.
            new_row = old_cols - 1 - old_col
            new_col = old_row

        elif delta == -90:
            # Поворот по часовой стрелке.
            new_row = old_col
            new_col = old_rows - 1 - old_row

        else:
            return

        # Меняем угол поворота.
        self.rotation_angle = (
                                      self.rotation_angle + delta
                              ) % 360

        # Рассчитываем индекс того же участка
        # уже в новой сетке.
        new_rows, new_cols = self._get_effective_grid()

        self.current_page = (
                new_row * new_cols + new_col
        )

        self._rebuild_tiles(reset_page=False)
        self._redraw_preview()

    def _rotate_left(self):
        self._rotate_image_by(90)

    def _rotate_right(self):
        self._rotate_image_by(-90)

    def _render_preview(self, tile, layout, mode):
        # Fixed logical canvas; geometry scales A4 uniformly and centers it.
        preview_w, preview_h = 620, 680
        geom = calculate_preview_geometry(
            tile.width if tile else 1,
            tile.height if tile else 1,
            layout, mode,
            preview_width=preview_w, preview_height=preview_h, padding=18
        )
        page_x, page_y, page_w, page_h = geom.page_rect
        canvas_img = Image.new("RGB", (preview_w, preview_h), (238, 240, 243))
        draw = ImageDraw.Draw(canvas_img)
        page_box = (round(page_x), round(page_y),
                    round(page_x + page_w), round(page_y + page_h))
        draw.rectangle(page_box, fill="white", outline=(65, 70, 78), width=2)

        mx, my, mw, mh = geom.printable_rect
        printable_box = (round(mx), round(my), round(mx + mw), round(my + mh))
        draw.rectangle(printable_box, outline=(205, 65, 55), width=2)

        if tile is not None:
            ix, iy, iw, ih = geom.image_rect
            target_w, target_h = max(1, round(iw)), max(1, round(ih))
            resized = tile.resize((target_w, target_h), Image.Resampling.LANCZOS)
            paste_x, paste_y = round(ix), round(iy)

            if mode == "fill":
                clip_left, clip_top, clip_right, clip_bottom = printable_box
                image_left, image_top = paste_x, paste_y
                image_right, image_bottom = paste_x + target_w, paste_y + target_h
                inter_left = max(clip_left, image_left)
                inter_top = max(clip_top, image_top)
                inter_right = min(clip_right, image_right)
                inter_bottom = min(clip_bottom, image_bottom)
                if inter_right > inter_left and inter_bottom > inter_top:
                    crop = resized.crop((
                        inter_left - image_left, inter_top - image_top,
                        inter_right - image_left, inter_bottom - image_top
                    ))
                    canvas_img.paste(crop, (inter_left, inter_top))
            else:
                canvas_img.paste(resized, (paste_x, paste_y))

            draw = ImageDraw.Draw(canvas_img)
            draw.rectangle(printable_box, outline=(205, 65, 55), width=2)
        else:
            draw.text((preview_w // 2 - 80, preview_h // 2), "pu-pu-pu", fill=(90, 95, 105))
        return canvas_img

    def _redraw_preview(self):
        try:
            layout = self._make_layout()
            mode = self._current_mode()
            tile = self.tiles[self.current_page] if self.tiles else None
            rendered = self._render_preview(tile, layout, mode)
            self._preview_photo = ImageTk.PhotoImage(rendered)
            self.preview_label.configure(image=self._preview_photo)

            total = len(self.tiles)
            if total:
                self.page_label_var.set(
                    f"Страница {self.current_page + 1} из {total}"
                )
                self.status_var.set(
                    f"{self.source_image.width} × {self.source_image.height} px · "
                    f"фрагмент {tile.width} × {tile.height} px · {mode}"
                )
            else:
                self.page_label_var.set("Страница — из —")
                self.status_var.set("Откройте изображение, чтобы начать.")

            self.prev_button.configure(state=("normal" if self.tiles and self.current_page > 0 else "disabled"))
            self.next_button.configure(
                state=("normal" if self.tiles and self.current_page < len(self.tiles) - 1 else "disabled")
            )
        except (ValueError, TypeError) as exc:
            self.status_var.set(f"Проверьте настройки: {exc}")
        except Exception as exc:
            self.status_var.set(f"Ошибка предпросмотра: {exc}")

    def _export_pdf(self):
        if not self.tiles:
            messagebox.showinfo("Нет изображения", "Сначала откройте изображение.", parent=self.root)
            return
        try:
            layout = self._make_layout()
            mode = self._current_mode()
        except Exception as exc:
            messagebox.showerror("Проверьте настройки", str(exc), parent=self.root)
            return

        default_name = Path(self.source_path).stem + "_poster.pdf" if self.source_path else "poster.pdf"
        path = filedialog.asksaveasfilename(
            title="Сохранить постер в PDF",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF-документ", "*.pdf")],
        )
        if not path:
            return
        try:
            export_tiles_to_pdf(self.tiles, layout, path, mode=mode)
            messagebox.showinfo(
                "Экспорт завершён",
                f"PDF сохранён:\n{path}\n\nКоличество страниц: {len(self.tiles)}",
                parent=self.root
            )
        except Exception as exc:
            messagebox.showerror("Ошибка экспорта", str(exc), parent=self.root)


def main():
    root = tk.Tk()
    PosterPrintApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
