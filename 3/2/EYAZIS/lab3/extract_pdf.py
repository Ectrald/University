import pdfplumber

text = ""
try:
    with pdfplumber.open(r"c:\University\3\2\EYAZIS\lab3\Лабораторная работа 3.pdf") as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    with open(r"c:\University\3\2\EYAZIS\lab3\pdf_content_lab3.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("PDF extraction successful.")
except Exception as e:
    print(f"Error: {e}")
