from typing import Dict, Any, List
import io

import fitz  


def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    pages: List[str] = []

    with fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf") as doc:
        for page in doc:
            text = page.get_text("text")
            if text is None:
                text = ""
            pages.append(text)

    full_text = "\n\n".join(pages)
    has_text = any(p.strip() for p in pages)

    return {
        "pages": pages,
        "full_text": full_text,
        "has_text": has_text,
    }
