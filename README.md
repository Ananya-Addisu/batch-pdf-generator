# Batch PDF Generator

A Python GUI application that generates PDF certificates from a template by overlaying names onto a user-specified region. The application lets you upload a PDF template, visually select where names should appear, enter multiple names, and generate individual certificates with a modern dark-themed UI.

## Features

- **Template Upload:** Load a PDF certificate template.
- **Region Selection:** Select the area on the template where the names will be placed.
- **Bulk Certificate Generation:** Enter a list of names (one per line) and automatically generate a personalized certificate for each.
- **Modern Dark UI:** Enjoy a sleek, dark-themed interface.
- **PDF Processing:** Uses libraries like `pdf2image`, `Pillow`, `ReportLab`, and `PyPDF2` to handle PDF manipulation.

## Requirements (Libraries)

- **Python 3.x**
- **Tkinter:** Typically included with Python.
- **[pdf2image](https://github.com/Belval/pdf2image)**
- **[Pillow](https://pillow.readthedocs.io/)**
- **[ReportLab](https://www.reportlab.com/)**
- **[PyPDF2](https://pypi.org/project/PyPDF2/)**

### Additional Requirement: Poppler

`pdf2image` requires [Poppler](https://poppler.freedesktop.org/) to convert PDF pages into images.

- **Windows:**  
  Download the binaries from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) and add the `bin` folder to your system's PATH.
- **macOS:**  
  Install via Homebrew:
  ```bash
  brew install poppler
