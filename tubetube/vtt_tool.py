import os
import re


class VttSubtitleTool:
    _BLOCK_SPLIT_RE = re.compile(r"\n\s*\n")
    _TAG_RE = re.compile(r"<[^>]+>")
    _TIMESTAMP_LINE_RE = re.compile(
        r"^\s*\d{1,2}:\d{2}(?::\d{2})?\.\d{3}\s+-->\s+\d{1,2}:\d{2}(?::\d{2})?\.\d{3}(?:\s+.*)?$"
    )

    def list_vtt_files(self, directory):
        try:
            entries = os.listdir(directory)
        except OSError:
            return []

        vtt_files = []
        for name in entries:
            if not name.lower().endswith(".vtt"):
                continue
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                vtt_files.append(path)
        return sorted(vtt_files)

    def extract_text_from_directory(self, directory):
        texts = []
        for file_path in self.list_vtt_files(directory):
            text = self.extract_text_from_file(file_path)
            if text:
                texts.append(text)
        return " ".join(texts).strip()

    def extract_texts_by_file(self, directory):
        results = {}
        for file_path in self.list_vtt_files(directory):
            results[file_path] = self.extract_text_from_file(file_path)
        return results

    def extract_text_from_file(self, file_path):
        content = self._read_file(file_path)
        return self.extract_text_from_vtt(content)

    def extract_text_from_vtt(self, content):
        if not content:
            return ""

        normalized = content.replace("\r\n", "\n").replace("\r", "\n")
        blocks = self._BLOCK_SPLIT_RE.split(normalized.strip())
        texts = []

        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if not lines:
                continue
            first = lines[0]
            if first.startswith("WEBVTT") or first.startswith("NOTE") or first.startswith("STYLE") or first.startswith("REGION"):
                continue

            time_index = None
            for idx, line in enumerate(lines):
                if self._TIMESTAMP_LINE_RE.match(line):
                    time_index = idx
                    break
            if time_index is None:
                continue

            for text_line in lines[time_index + 1 :]:
                cleaned = self._clean_text_line(text_line)
                if cleaned:
                    texts.append(cleaned)

        return " ".join(texts).strip()

    def _read_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8-sig", errors="replace") as handle:
                return handle.read()
        except OSError:
            return ""

    def _clean_text_line(self, line):
        if not line:
            return ""
        line = self._TAG_RE.sub("", line)
        return re.sub(r"\s+", " ", line).strip()
