# PosterPrint

PosterPrint is a Python desktop application for preparing large images and documents for printing across multiple A4 sheets.
The application splits source materials into a configurable grid of pages, allowing users to print posters using a standard printer.

PosterPrint — это настольное приложение на языке Python, предназначенное для подготовки крупных изображений и документов к печати на нескольких листах формата A4.
Приложение разбивает исходные материалы на настраиваемую сетку страниц, позволяя пользователям распечатывать плакаты на обычном принтере.

## Features/Особенности

- Import images: PNG, JPG, JPEG, BMP, WEBP, TIFF./Импорт изображения формата: PNG, JPG, JPEG, BMP, WEBP, TIFF.
  

- Import PDF documents with page selection./Импорт PDF документы с выбором страницы.
  

- Import DOCX documents with page selection./Импорт DOCX документы с выбором страницы.
  

- Split images into configurable page grids:/Делит исходное изображение на сетку:
  - 2 × 2
  - 3 × 3
  - 4 × 4

- Image placement modes:/Поддерживаемые режимы:
  - Fit (вставить)
  - Fill (Заполнить)
  - Stretch (Растянуть)

- Rotate the entire poster./Поворот всего постера

- Preview individual pages before exporting./Предварительный просмотр фрагментов перед экспортом

- Export prepared pages to PDF./Экспорт результата в PDF файл.


## Technologies/Технологии

- Python 3.12
- Tkinter
- Pillow
- ReportLab
- PyMuPDF
- dxpdf

## Installation/Установка

1. Clone the repository:

   git clone YOUR_REPOSITORY_URL
   cd PosterPrint
   

2. Create a virtual environment:

   python -m venv .venv
   

3. Activate the environment:

   Windows:
   .venv\Scripts\activate
   

4. Install dependencies:

   python -m pip install -r requirements.txt


## Running the application/Запуск приложения


python app.py


## License/Лицензия

This project is licensed under the MIT License. See the `LICENSE` file for details.

Этот проект распространяется по лицензии MIT. Подробности см. в файле `LICENSE`.