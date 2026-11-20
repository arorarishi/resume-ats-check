import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypdf import PdfWriter
from app.parsers.pdf_parser import extract_text_from_pdf

# Create a sample PDF in memory
writer = PdfWriter()
page = writer.add_blank_page(width=612, height=792)

# Save to buffer
buf = io.BytesIO()
writer.write(buf)
buf.seek(0)

# Test parser
res = extract_text_from_pdf(buf.getvalue())
assert res["page_count"] == 1
print("PDF Parser initialized and validated successfully!")
