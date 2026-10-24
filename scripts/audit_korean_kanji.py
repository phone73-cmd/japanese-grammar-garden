#!/usr/bin/env python3
"""Build a reviewed-ready 625-kanji Korean reading audit from official KANJIDIC2.
Usage: python scripts/audit_korean_kanji.py /path/to/kanjidic2.xml.gz
Never edits the app's existing kanji source or user records.
"""
import hashlib
import argparse
import gzip
import json
import pathlib
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = [ROOT / "data/kanji" / f"kanji-stage-{i}-100.draft.json" for i in range(1, 6)]
SOURCES.append(ROOT / "data/kanji/kanji-extra-125.draft.json")
OUTPUT = ROOT / "data/kanji/kanji-korean-readings.audit.json"
REPORT = ROOT / "data/kanji/KOREAN-READINGS-AUDIT.md"

def unique(seq):
    return list(dict.fromkeys(seq))

def load_dictionary(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    result = {}
    with opener(path, "rb") as stream:
        for _, element in ET.iterparse(stream, events=("end",)):
            if element.tag != "character":
                continue
            literal = element.findtext("literal")
            readings = {"korean_h": [], "ja_on": [], "ja_kun": []}
            for node in element.findall("./reading_meaning/rmgroup/reading"):
                typ = node.attrib.get("r_type")
                if typ in readings and node.text:
                    readings[typ].append(node.text.strip())
            result[literal] = {key: unique(value) for key, value in readings.items()}
            element.clear()
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kanjidic2", type=pathlib.Path, help="Official KANJIDIC2 XML or XML.gz")
    args = parser.parse_args()
    data = []
    for path in SOURCES:
        group = json.loads(path.read_text(encoding="utf-8"))["items"]
        expected = 125 if "extra-125" in path.name else 100
        if len(group) != expected:
            raise SystemExit(f"Unexpected count in {path}: {len(group)}")
        data.extend(group)
    if len(data) != 625 or len({x["id"] for x in data}) != 625 or len({x["character"] for x in data}) != 625:
        raise SystemExit("Expected 625 unique kanji IDs and characters; no output written")
    dictionary = load_dictionary(args.kanjidic2)
    results = []
    for item in data:
        char = item["character"]
        entry = dictionary.get(char)
        source_on = item.get("on_readings", [])
        source_kun = item.get("kun_readings", [])
        status = "matched" if entry else "not_in_kanjidic2"
        on_missing = [x for x in source_on if entry and x not in entry["ja_on"]]
        kun_missing = [x for x in source_kun if entry and x not in entry["ja_kun"]]
        if entry and (on_missing or kun_missing):
            status = "reading_mismatch_review"
        if entry and not entry["korean_h"]:
            status = "korean_reading_missing" if status == "matched" else status
        results.append({
            "id": item["id"], "character": char, "stage": item["stage"],
            "meaning_ko_existing": item.get("meaning_ko"),
            "korean_readings": entry["korean_h"] if entry else [],
            "korean_gloss": None,
            "japanese_on_existing": source_on,
            "japanese_kun_existing": source_kun,
            "japanese_on_dictionary": entry["ja_on"] if entry else [],
            "japanese_kun_dictionary": entry["ja_kun"] if entry else [],
            "on_not_in_dictionary": on_missing,
            "kun_not_in_dictionary": kun_missing,
            "status": status,
            "korean_gloss_review": "pending",
        })
    counts = Counter(x["status"] for x in results)
    payload = {
        "schema": "jgg-kanji-korean-audit-v1",
        "source": "EDRDG KANJIDIC2 (korean_h, ja_on, ja_kun); CC BY-SA 4.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total": 625, "status_counts": dict(counts),
        "source_sha256": hashlib.sha256(args.kanjidic2.read_bytes()).hexdigest(),
        "source_url": "https://www.edrdg.org/kanjidic/kanjidic2.xml.gz",
        "scope": "Raw KANJIDIC2 only. Final Korean gloss/variant/word connections are in kanji-enrichment.json.",
        "note": "Korean glosses are NOT derived from KANJIDIC2. Review before displaying in UI.",
        "items": results,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    flagged = [x for x in results if x["status"] != "matched"]
    lines = [
        "# 625자 한국 한자음·일본어 읽기 대조 보고서",
        "", "사전: EDRDG KANJIDIC2 · CC BY-SA 4.0",
        "", "이 파일은 KANJIDIC2만 사용한 원시 자동 대조 결과입니다. 최종 훈·음·표기·단어 연결 및 개별 예외 확인은 kanji-enrichment.json과 KANJI-ENRICHMENT-AUDIT.md를 참조하세요.",
        "", f"- 총 글자: {len(results)}", f"- 사전 미수록: {counts['not_in_kanjidic2']}",
        f"- 읽기 불일치: {counts['reading_mismatch_review']}",
        f"- 한국 한자음 누락: {counts['korean_reading_missing']}",
        f"- 일치: {counts['matched']}",
        "", "## 수동 검토 대상", "",
        "| ID | 한자 | 상태 | 기존 음독 중 불일치 | 기존 훈독 중 불일치 |",
        "|---|---|---|---|---|",
    ]
    for x in flagged:
        lines.append(f"| {x['id']} | {x['character']} | {x['status']} | {', '.join(x['on_not_in_dictionary'])} | {', '.join(x['kun_not_in_dictionary'])} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Audited {len(results)} characters: {dict(counts)}")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} and {REPORT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()

