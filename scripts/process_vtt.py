import os
import re
import sys

from tubetube.vtt_tool import VttSubtitleTool


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VTT_DIR = os.path.join(REPO_ROOT, "data", "Video")
DEFAULT_FILENAME = "x.vtt"


def _convert_to_simplified(text):
    try:
        from opencc import OpenCC
    except ImportError:
        print(
            "Missing dependency: opencc. Install opencc-python-reimplemented to enable t2s conversion.",
            file=sys.stderr,
        )
        return "", 1

    converter = OpenCC("t2s") # 繁体转简体
    return converter.convert(text), 0


def _format_paragraphs(text, min_len=80, max_len=120):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""

    sentence_enders = set("。！？!?；;")
    soft_enders = set("，,、:：")
    paragraphs = []
    start = 0
    total_len = len(text)

    while start < total_len:
        remaining = total_len - start
        if remaining <= max_len:
            paragraphs.append(text[start:].strip())
            break

        end = start + max_len
        window = text[start:end]
        break_pos = -1

        for idx in range(len(window) - 1, min_len - 2, -1):
            if window[idx] in sentence_enders:
                break_pos = idx + 1
                break

        if break_pos == -1:
            for idx in range(len(window) - 1, min_len - 2, -1):
                if window[idx] in soft_enders:
                    break_pos = idx + 1
                    break

        if break_pos == -1:
            for idx in range(len(window) - 1, min_len - 2, -1):
                if window[idx].isspace():
                    break_pos = idx + 1
                    break

        if break_pos == -1:
            break_pos = min_len

        paragraph = text[start : start + break_pos].strip()
        if paragraph:
            paragraphs.append(paragraph)
        start += break_pos
        while start < total_len and text[start].isspace():
            start += 1

    return "\n\n".join(paragraphs)


def process_vtt(filename=DEFAULT_FILENAME):
    vtt_path = os.path.join(VTT_DIR, filename)
    if not os.path.isfile(vtt_path):
        print(f"VTT file not found: {vtt_path}", file=sys.stderr)
        return "", 1

    tool = VttSubtitleTool()
    text = tool.extract_text_from_file(vtt_path)
    text, status = _convert_to_simplified(text)
    if status != 0:
        return "", status
    text = _format_paragraphs(text)
    return text, 0


if __name__ == "__main__":
    filename = "test.vtt"
    text, status = process_vtt(filename)
    if status == 0:
        print(text)
    raise SystemExit(status)
