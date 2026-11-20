import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import docx
from app.parsers.docx_parser import extract_text_from_docx

doc = docx.Document()
doc.add_heading("John Doe Resume", 0)
doc.add_paragraph("Senior Python Developer | john@example.com")
p = doc.add_paragraph()
p.add_run("Skills: Python, FastAPI, Docker, PostgreSQL")

buf = io.BytesIO()
doc.save(buf)
buf.seek(0)

res = extract_text_from_docx(buf.getvalue())
assert "John Doe Resume" in res["text"]
assert "FastAPI" in res["text"]
print("DOCX Parser initialized and validated successfully!")
