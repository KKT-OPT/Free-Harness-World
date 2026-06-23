import os
import re
import sys
import zlib


WS = b" \t\r\n\f\x00"


def decompress_stream(raw):
    for candidate in (raw, raw.strip(b"\r\n")):
        try:
            return zlib.decompress(candidate)
        except Exception:
            pass
    return None


def iter_direct_objects(data):
    pattern = re.compile(rb"(?m)(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj\b", re.S)
    for match in pattern.finditer(data):
        yield int(match.group(1)), match.group(3)


def split_stream_object(body):
    match = re.search(rb"\bstream\r?\n", body)
    if not match:
        return body, None
    start = match.end()
    end = body.rfind(b"endstream")
    if end < start:
        return body, None
    return body[: match.start()], body[start:end]


def parse_object_stream(obj_body, stream_data):
    first = re.search(rb"/First\s+(\d+)", obj_body)
    count = re.search(rb"/N\s+(\d+)", obj_body)
    if not first or not count or stream_data is None:
        return {}
    first = int(first.group(1))
    count = int(count.group(1))
    header = stream_data[:first]
    payload = stream_data[first:]
    nums = [int(x) for x in re.findall(rb"\d+", header)]
    out = {}
    pairs = list(zip(nums[0::2], nums[1::2]))[:count]
    for idx, (obj_num, offset) in enumerate(pairs):
        next_offset = pairs[idx + 1][1] if idx + 1 < len(pairs) else len(payload)
        out[obj_num] = payload[offset:next_offset].strip()
    return out


def build_pdf_objects(data):
    objects = {}
    streams = {}
    stream_dicts = {}

    for obj_num, body in iter_direct_objects(data):
        obj_dict, stream_raw = split_stream_object(body)
        objects[obj_num] = obj_dict.strip()
        if stream_raw is not None:
            decoded = decompress_stream(stream_raw) if b"/FlateDecode" in obj_dict else stream_raw
            streams[obj_num] = decoded
            stream_dicts[obj_num] = obj_dict

    # Expand compressed object streams.
    changed = True
    while changed:
        changed = False
        for obj_num, obj_dict in list(objects.items()):
            if b"/ObjStm" not in obj_dict or obj_num not in streams:
                continue
            for inner_num, inner_body in parse_object_stream(obj_dict, streams[obj_num]).items():
                if inner_num not in objects:
                    objects[inner_num] = inner_body
                    changed = True

    return objects, streams, stream_dicts


def parse_utf16_hex(hex_text):
    raw = bytes.fromhex(hex_text.decode("ascii", "ignore"))
    if raw.startswith(b"\xfe\xff"):
        raw = raw[2:]
    try:
        return raw.decode("utf-16-be", "replace")
    except Exception:
        try:
            return raw.decode("latin1", "replace")
        except Exception:
            return ""


def parse_cmap(cmap_bytes):
    text = cmap_bytes.decode("latin1", "ignore")
    cmap = {}

    bfchar = re.compile(r"beginbfchar(.*?)endbfchar", re.S)
    bfrange = re.compile(r"beginbfrange(.*?)endbfrange", re.S)

    for block in bfchar.findall(text):
        for src, dst in re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>", block):
            try:
                cmap[bytes.fromhex(src)] = parse_utf16_hex(dst.encode("ascii"))
            except Exception:
                pass

    for block in bfrange.findall(text):
        for line in block.splitlines():
            line = line.strip()
            if not line or not line.startswith("<"):
                continue
            range_match = re.match(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>\s+(.*)", line)
            if not range_match:
                continue
            start_hex, end_hex, rest = range_match.groups()
            try:
                start = int(start_hex, 16)
                end = int(end_hex, 16)
                width = len(start_hex) // 2
            except Exception:
                continue
            array_values = re.findall(r"<([0-9A-Fa-f]+)>", rest)
            if rest.startswith("["):
                for idx, dst in enumerate(array_values):
                    key = (start + idx).to_bytes(width, "big")
                    cmap[key] = parse_utf16_hex(dst.encode("ascii"))
            elif array_values:
                try:
                    dst_start = int(array_values[0], 16)
                    dst_width = len(array_values[0]) // 2
                    for code in range(start, end + 1):
                        key = code.to_bytes(width, "big")
                        dst = (dst_start + (code - start)).to_bytes(dst_width, "big")
                        cmap[key] = dst.decode("utf-16-be", "replace")
                except Exception:
                    pass
    return cmap


PDF_DOC_ENCODING = {
    0x18: "\u02d8",
    0x19: "\u02c7",
    0x1A: "\u02c6",
    0x1B: "\u02d9",
    0x1C: "\u02dd",
    0x1D: "\u02db",
    0x1E: "\u02da",
    0x1F: "\u02dc",
    0x7F: "",
    0x80: "\u2022",
    0x81: "\u2020",
    0x82: "\u2021",
    0x83: "\u2026",
    0x84: "\u2014",
    0x85: "\u2013",
    0x86: "\u0192",
    0x87: "\u2044",
    0x88: "\u2039",
    0x89: "\u203a",
    0x8A: "\u2212",
    0x8B: "\u2030",
    0x8C: "\u201e",
    0x8D: "\u201c",
    0x8E: "\u201d",
    0x8F: "\u2018",
    0x90: "\u2019",
    0x91: "\u201a",
    0x92: "\u2122",
    0x93: "\ufb01",
    0x94: "\ufb02",
    0x95: "\u0141",
    0x96: "\u0152",
    0x97: "\u0160",
    0x98: "\u0178",
    0x99: "\u017d",
    0x9A: "\u0131",
    0x9B: "\u0142",
    0x9C: "\u0153",
    0x9D: "\u0161",
    0x9E: "\u017e",
    0xA0: "\u20ac",
}


def pdfdoc_decode(raw):
    return "".join(PDF_DOC_ENCODING.get(b, chr(b)) for b in raw)


def decode_pdf_string(raw, cmap):
    if not raw:
        return ""
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", "replace")
    if cmap:
        lengths = sorted({len(k) for k in cmap}, reverse=True)
        out = []
        i = 0
        while i < len(raw):
            matched = False
            for size in lengths:
                piece = raw[i : i + size]
                if piece in cmap:
                    out.append(cmap[piece])
                    i += size
                    matched = True
                    break
            if not matched:
                out.append(pdfdoc_decode(raw[i : i + 1]))
                i += 1
        return "".join(out)
    try:
        return pdfdoc_decode(raw)
    except Exception:
        return raw.decode("latin1", "replace")


def parse_literal_string(data, i):
    assert data[i] == 40
    i += 1
    depth = 1
    out = bytearray()
    while i < len(data) and depth:
        ch = data[i]
        if ch == 92:
            i += 1
            if i >= len(data):
                break
            esc = data[i]
            lookup = {
                ord("n"): b"\n",
                ord("r"): b"\r",
                ord("t"): b"\t",
                ord("b"): b"\b",
                ord("f"): b"\f",
                ord("("): b"(",
                ord(")"): b")",
                ord("\\"): b"\\",
            }
            if esc in lookup:
                out.extend(lookup[esc])
                i += 1
            elif 48 <= esc <= 55:
                octal = bytes([esc])
                i += 1
                for _ in range(2):
                    if i < len(data) and 48 <= data[i] <= 55:
                        octal += bytes([data[i]])
                        i += 1
                    else:
                        break
                out.append(int(octal, 8))
            elif esc in (10, 13):
                if esc == 13 and i + 1 < len(data) and data[i + 1] == 10:
                    i += 2
                else:
                    i += 1
            else:
                out.append(esc)
                i += 1
        elif ch == 40:
            depth += 1
            out.append(ch)
            i += 1
        elif ch == 41:
            depth -= 1
            if depth:
                out.append(ch)
            i += 1
        else:
            out.append(ch)
            i += 1
    return bytes(out), i


def parse_hex_string(data, i):
    assert data[i] == 60
    i += 1
    start = i
    while i < len(data) and data[i] != 62:
        i += 1
    hex_text = re.sub(rb"\s+", b"", data[start:i])
    if len(hex_text) % 2:
        hex_text += b"0"
    try:
        raw = bytes.fromhex(hex_text.decode("ascii", "ignore"))
    except Exception:
        raw = b""
    return raw, i + 1


def tokenize_content(data):
    i = 0
    while i < len(data):
        ch = data[i]
        if ch in WS:
            i += 1
            continue
        if ch == 37:  # comment
            while i < len(data) and data[i] not in b"\r\n":
                i += 1
            continue
        if ch == 40:
            val, i = parse_literal_string(data, i)
            yield ("string", val)
            continue
        if ch == 60 and i + 1 < len(data) and data[i + 1] != 60:
            val, i = parse_hex_string(data, i)
            yield ("string", val)
            continue
        if ch == 60 and i + 1 < len(data) and data[i + 1] == 60:
            yield ("dict_start", "<<")
            i += 2
            continue
        if ch == 62 and i + 1 < len(data) and data[i + 1] == 62:
            yield ("dict_end", ">>")
            i += 2
            continue
        if ch == 47:
            start = i
            i += 1
            while i < len(data) and data[i] not in WS + b"[]<>()/":
                i += 1
            yield ("name", data[start:i].decode("latin1", "replace"))
            continue
        if ch in b"[]":
            yield (chr(ch), chr(ch))
            i += 1
            continue
        start = i
        while i < len(data) and data[i] not in WS + b"[]<>()/":
            i += 1
        token = data[start:i].decode("latin1", "replace")
        if token:
            yield ("atom", token)


TEXT_OPERATORS = {
    "Tj",
    "TJ",
    "'",
    '"',
    "Tf",
    "Td",
    "TD",
    "Tm",
    "T*",
    "ET",
    "BT",
}


def extract_text_from_content(data, font_cmaps):
    out = []
    stack = []
    current_font = None
    array_depth = 0

    def cmap_for_current():
        return font_cmaps.get(current_font, {})

    def append_text(raw):
        text = decode_pdf_string(raw, cmap_for_current())
        if text:
            out.append(text)

    for typ, val in tokenize_content(data):
        if typ == "[":
            stack.append(("array_start", None))
            array_depth += 1
            continue
        if typ == "]":
            arr = []
            while stack and stack[-1][0] != "array_start":
                arr.append(stack.pop())
            if stack and stack[-1][0] == "array_start":
                stack.pop()
            array_depth = max(0, array_depth - 1)
            arr.reverse()
            stack.append(("array", arr))
            continue

        if typ == "atom" and val in TEXT_OPERATORS:
            if val == "Tf" and len(stack) >= 2:
                font = stack[-2]
                if font[0] == "name":
                    current_font = font[1]
            elif val == "Tj" and stack:
                arg = stack[-1]
                if arg[0] == "string":
                    append_text(arg[1])
            elif val == "TJ" and stack:
                arg = stack[-1]
                if arg[0] == "array":
                    for item_type, item_val in arg[1]:
                        if item_type == "string":
                            append_text(item_val)
                        elif item_type == "atom":
                            try:
                                if float(item_val) < -180:
                                    out.append(" ")
                            except Exception:
                                pass
            elif val == "'":
                out.append("\n")
                if stack and stack[-1][0] == "string":
                    append_text(stack[-1][1])
            elif val == '"':
                out.append("\n")
                if stack and stack[-1][0] == "string":
                    append_text(stack[-1][1])
            elif val in ("Td", "TD", "T*", "Tm", "ET"):
                out.append("\n")
            stack = []
            continue

        # Outside text arrays, any non-numeric atom is a PDF graphics/state operator
        # for our purposes. Clearing here prevents long drawing command streams from
        # accumulating thousands of irrelevant operands before the next text operator.
        if typ == "atom" and array_depth == 0 and not is_number_token(val):
            stack = []
            continue

        stack.append((typ, val))

    text = "".join(out)
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def is_number_token(token):
    try:
        float(token)
        return True
    except Exception:
        return False


def build_font_cmaps(objects, streams):
    cmaps_by_obj = {
        obj_num: parse_cmap(data)
        for obj_num, data in streams.items()
        if data and b"begincmap" in data
    }
    font_obj_to_cmap = {}
    for obj_num, obj in objects.items():
        match = re.search(rb"/ToUnicode\s+(\d+)\s+\d+\s+R", obj)
        if match:
            cmap_obj = int(match.group(1))
            font_obj_to_cmap[obj_num] = cmaps_by_obj.get(cmap_obj, {})

    font_cmaps = {}
    font_section = re.compile(rb"/Font\s*<<(.*?)>>", re.S)
    font_ref = re.compile(rb"/([A-Za-z0-9_.@+-]+)\s+(\d+)\s+\d+\s+R")
    for obj in objects.values():
        for section in font_section.findall(obj):
            for name, font_obj in font_ref.findall(section):
                key = "/" + name.decode("latin1", "replace")
                cmap = font_obj_to_cmap.get(int(font_obj), {})
                if cmap:
                    font_cmaps[key] = cmap
    return font_cmaps


def extract_pdf(path):
    data = open(path, "rb").read()
    objects, streams, stream_dicts = build_pdf_objects(data)
    font_cmaps = build_font_cmaps(objects, streams)
    parts = []
    for obj_num in sorted(streams):
        stream = streams[obj_num]
        obj_dict = stream_dicts.get(obj_num, b"")
        if not stream:
            continue
        if (
            b"BT" not in stream
            or b"/ObjStm" in obj_dict
            or b"/Subtype /Image" in obj_dict
            or b"/FontFile" in obj_dict
            or b"/CIDSet" in obj_dict
            or b"/Metadata" in obj_dict
            or b"begincmap" in stream
            or not is_probably_ascii_content(stream)
        ):
            continue
        text = extract_text_from_content(stream, font_cmaps)
        cleaned = text.strip()
        if len(cleaned) >= 20:
            parts.append(cleaned)
    final = "\n\n".join(parts)
    final = final.replace("\ufb01", "fi").replace("\ufb02", "fl")
    final = re.sub(r"[ \t]+\n", "\n", final)
    final = re.sub(r"\n{4,}", "\n\n\n", final)
    return final


def is_probably_ascii_content(stream):
    sample = stream[: min(len(stream), 12000)]
    if not sample:
        return False
    printable = sum(1 for b in sample if b in b"\r\n\t" or 32 <= b <= 126)
    return printable / float(len(sample)) > 0.80


def main(argv):
    if len(argv) < 3:
        raise SystemExit("usage: extract_pdf_text.py OUTPUT_DIR PDF...")
    out_dir = argv[1]
    os.makedirs(out_dir, exist_ok=True)
    for path in argv[2:]:
        text = extract_pdf(path)
        base = os.path.splitext(os.path.basename(path))[0]
        out_path = os.path.join(out_dir, base + ".txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{out_path}\t{len(text)} chars")


if __name__ == "__main__":
    main(sys.argv)
