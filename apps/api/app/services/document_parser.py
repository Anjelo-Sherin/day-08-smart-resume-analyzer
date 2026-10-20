"""Multi-format Resume Document Parser (.pdf, .docx, .txt, .md) and Pure-Python PDF Generator."""

import io
import re
import xml.etree.ElementTree as ET
import zipfile
import zlib


def _decode_pdf_literal_string(raw: str) -> str:
    """Unescape PDF literal string escapes like \\(, \\), \\n, and octal sequences."""
    out = []
    i = 0
    n = len(raw)
    while i < n:
        ch = raw[i]
        if ch == "\\" and i + 1 < n:
            nxt = raw[i + 1]
            if nxt in ("(", ")", "\\"):
                out.append(nxt)
                i += 2
            elif nxt == "n":
                out.append("\n")
                i += 2
            elif nxt == "r":
                out.append("\r")
                i += 2
            elif nxt == "t":
                out.append("\t")
                i += 2
            elif nxt.isdigit():
                octal = raw[i + 1 : i + 4]
                m = re.match(r"^[0-7]{1,3}", octal)
                if m:
                    out.append(chr(int(m.group(0), 8)))
                    i += 1 + len(m.group(0))
                else:
                    i += 2
            else:
                out.append(nxt)
                i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _extract_text_from_pdf_stream(content_str: str) -> list[str]:
    """Extract text operators (Tj, TJ, ', \") from a decompressed PDF content stream."""
    lines: list[str] = []
    current_line: list[str] = []

    # Match BT ... ET text blocks or scan entire stream if BT/ET spans across chunks
    blocks = re.findall(r"BT(.*?)ET", content_str, flags=re.DOTALL)
    targets = blocks if blocks else [content_str]

    token_pattern = re.compile(
        r"(\[(?:[^\[\]]|\((?:\\.|[^\\\)])*\))*\]\s*TJ|\((?:\\.|[^\\\)])*\)\s*(?:Tj|'|\"\s*)|T\*|Td|TD|Tm)",
        flags=re.DOTALL,
    )
    literal_pattern = re.compile(r"\((?:\\.|[^\\\)])*\)")

    for block in targets:
        for match in token_pattern.finditer(block):
            tok = match.group(0).strip()
            if tok in ("T*", "Td", "TD", "Tm"):
                if current_line:
                    lines.append("".join(current_line).strip())
                    current_line = []
            elif tok.endswith("TJ"):
                parts = [
                    _decode_pdf_literal_string(m.group(0)[1:-1])
                    for m in literal_pattern.finditer(tok)
                ]
                current_line.append("".join(parts))
            else:
                m = literal_pattern.search(tok)
                if m:
                    current_line.append(_decode_pdf_literal_string(m.group(0)[1:-1]))
        if current_line:
            lines.append("".join(current_line).strip())
            current_line = []

    return [ln for ln in lines if ln]


def extract_text_from_pdf_bytes(data: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF (fitz), pypdf, or native stream parser."""
    # 1. Try PyMuPDF (fitz) if available
    try:
        import fitz  # type: ignore

        doc = fitz.open(stream=data, filetype="pdf")
        pages = [page.get_text("text") for page in doc]
        text = "\n".join(pages).strip()
        if text:
            return text
    except Exception:
        pass

    # 2. Try pypdf if available
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if text:
            return text
    except Exception:
        pass

    # 3. Built-in native PDF stream parser (handles FlateDecode & uncompressed PDF streams)
    extracted_lines: list[str] = []
    stream_pattern = re.compile(rb"stream[\r\n]+(.*?)[\r\n]+endstream", re.DOTALL)

    for match in stream_pattern.finditer(data):
        raw_stream = match.group(1)
        decoded_bytes = raw_stream
        for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS):
            try:
                decoded_bytes = zlib.decompress(raw_stream, wbits)
                break
            except Exception:
                continue
        text_chunk = decoded_bytes.decode("latin-1", errors="ignore")
        lines = _extract_text_from_pdf_stream(text_chunk)
        if lines:
            extracted_lines.extend(lines)

    if extracted_lines:
        return "\n".join(extracted_lines).strip()

    # Fallback: scan entire byte buffer for uncompressed text operators
    raw_latin = data.decode("latin-1", errors="ignore")
    fallback_lines = _extract_text_from_pdf_stream(raw_latin)
    if fallback_lines:
        return "\n".join(fallback_lines).strip()

    raise ValueError("Unable to extract readable text from PDF file.")


def extract_text_from_docx_bytes(data: bytes) -> str:
    """Extract text from DOCX bytes using python-docx or native OpenXML parser."""
    try:
        import docx  # type: ignore

        doc = docx.Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        if paragraphs:
            return "\n".join(paragraphs)
    except Exception:
        pass

    # Pure-Python OpenXML word/document.xml extraction
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            xml_bytes = zf.read("word/document.xml")
        root = ET.fromstring(xml_bytes)
        paragraphs = []
        for elem in root.iter():
            if elem.tag.endswith("}p"):
                texts = [
                    t.text
                    for t in elem.iter()
                    if t.tag.endswith("}t") and t.text
                ]
                para = "".join(texts).strip()
                if para:
                    paragraphs.append(para)
        return "\n".join(paragraphs).strip()
    except Exception as exc:
        raise ValueError(f"Invalid DOCX file: {exc}") from exc


def parse_uploaded_document(filename: str, content: bytes) -> str:
    """Dispatch document extraction based on file extension."""
    lower_name = (filename or "resume.txt").lower()
    if lower_name.endswith(".pdf") or content.startswith(b"%PDF"):
        return extract_text_from_pdf_bytes(content)
    if lower_name.endswith(".docx") or (content.startswith(b"PK\x03\x04") and b"word/" in content[:2000]):
        return extract_text_from_docx_bytes(content)
    return content.decode("utf-8", errors="replace").strip()


def generate_pdf_bytes(title: str, resume_text: str) -> bytes:
    """Generate a valid, standards-compliant multi-line PDF document in pure Python."""
    def _esc(txt: str) -> str:
        cleaned = txt.encode("ascii", errors="replace").decode("ascii")
        return cleaned.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    wrapped_lines: list[str] = [title]
    wrapped_lines.append("=" * min(len(title), 72))
    for raw_line in resume_text.splitlines():
        line = raw_line.strip()
        if not line:
            wrapped_lines.append("")
            continue
        while len(line) > 88:
            split_idx = line.rfind(" ", 0, 88)
            if split_idx <= 0:
                split_idx = 88
            wrapped_lines.append(line[:split_idx])
            line = line[split_idx:].strip()
        wrapped_lines.append(line)

    # Build content stream commands (up to 52 lines per page)
    lines_per_page = 48
    pages_lines = [
        wrapped_lines[i : i + lines_per_page]
        for i in range(0, max(1, len(wrapped_lines)), lines_per_page)
    ]

    objects: list[bytes] = []

    # Object 1: Catalog
    # Object 2: Pages
    # Object 3: Font (Helvetica)
    page_obj_ids: list[int] = []
    content_obj_ids: list[int] = []
    next_id = 4
    for _ in pages_lines:
        page_obj_ids.append(next_id)
        content_obj_ids.append(next_id + 1)
        next_id += 2

    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    kids_str = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
    objects.append(
        f"2 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {len(page_obj_ids)} >>\nendobj\n".encode("ascii")
    )
    objects.append(
        b"3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    )

    for idx, p_lines in enumerate(pages_lines):
        pid = page_obj_ids[idx]
        cid = content_obj_ids[idx]

        stream_cmds = ["BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
        for l_idx, ln in enumerate(p_lines):
            escaped = _esc(ln)
            if l_idx == 0:
                stream_cmds.append(f"({escaped}) Tj")
            else:
                stream_cmds.append(f"T* ({escaped}) Tj")
        stream_cmds.append("ET")
        stream_data = "\n".join(stream_cmds).encode("latin-1")
        compressed = zlib.compress(stream_data)

        page_obj = (
            f"{pid} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {cid} 0 R >>\n"
            f"endobj\n"
        ).encode("ascii")
        content_obj = (
            f"{cid} 0 obj\n<< /Length {len(compressed)} /Filter /FlateDecode >>\nstream\n".encode("ascii")
            + compressed
            + b"\nendstream\nendobj\n"
        )
        objects.append(page_obj)
        objects.append(content_obj)

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = [0]
    for obj in objects:
        offsets.append(len(out))
        out.extend(obj)

    xref_offset = len(out)
    out.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    out.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(out)
