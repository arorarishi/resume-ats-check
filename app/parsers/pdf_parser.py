import io
import re
from typing import List, Dict, Any
from pypdf import PdfReader

def extract_text_from_pdf(file_source) -> Dict[str, Any]:
    """
    Extracts text and metadata from PDF bytes or path.
    """
    if isinstance(file_source, bytes):
        stream = io.BytesIO(file_source)
    else:
        stream = file_source

    reader = PdfReader(stream)
    pages_text: List[str] = []
    total_pages = len(reader.pages)

    for idx, page in enumerate(reader.pages):
        try:
            page_content = page.extract_text() or ""
            # clean soft hyphens and weird spacing
            cleaned = re.sub(r'(\w+)-\n(\w+)', r'\1\2', page_content)
            pages_text.append(cleaned)
        except Exception as e:
            pages_text.append(f"[Error reading page {idx + 1}: {str(e)}]")

    full_text = "\n\n".join(pages_text).strip()

    # Basic layout indicators for ATS
    has_potential_multi_column = False
    for pt in pages_text:
        # crude heuristic: repeated large spaces within lines
        if re.search(r'[A-Za-z0-9]{3,}\s{5,}[A-Za-z0-9]{3,}', pt):
            has_potential_multi_column = True
            break

    return {
        "text": full_text,
        "page_count": total_pages,
        "multi_column_detected": has_potential_multi_column,
        "char_count": len(full_text)
    }
