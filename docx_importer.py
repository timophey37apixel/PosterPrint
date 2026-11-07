
from pathlib import Path


def convert_docx_to_pdf(docx_path, pdf_path):
    """Конвертирует DOCX-документ в PDF."""

    try:
        import dxpdf
    except ImportError as exc:
        raise ImportError(
            "Не найден модуль dxpdf"
        ) from exc

    docx_path = Path(docx_path)
    pdf_path = Path(pdf_path)

    if not docx_path.exists():
        raise FileNotFoundError(
            f"DOCX-файл не найден: {docx_path}"
        )

    dxpdf.convert_file(
        str(docx_path),
        str(pdf_path),
        image_dpi=300
    )
