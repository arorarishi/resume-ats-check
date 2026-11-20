import io
from typing import Dict, Any, List
import docx

def extract_text_from_docx(file_source) -> Dict[str, Any]:
    """
    Extracts text, table cells, and metadata from DOCX bytes or path.
    """
    if isinstance(file_source, bytes):
        stream = io.BytesIO(file_source)
    else:
        stream = file_source

    doc = docx.Document(stream)
    paragraphs_text: List[str] = []

    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt:
            paragraphs_text.append(txt)

    table_cells_count = 0
    # Also extract any tables (warn ATS user if tables contain core info)
    for table in doc.tables:
        for row in table.rows:
            row_texts = []
            for cell in row.cells:
                ct = cell.text.strip()
                if ct:
                    table_cells_count += 1
                    row_texts.append(ct)
            if row_texts:
                paragraphs_text.append(" | ".join(row_texts))

    full_text = "\n".join(paragraphs_text).strip()

    return {
        "text": full_text,
        "paragraph_count": len(doc.paragraphs),
        "tables_detected": len(doc.tables),
        "char_count": len(full_text)
    }
