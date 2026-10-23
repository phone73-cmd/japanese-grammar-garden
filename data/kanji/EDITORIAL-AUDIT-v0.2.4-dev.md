# Kanji vocabulary reading editorial audit — v0.2.4-dev

Date: 2026-10-23. This is a **triage report**, not a completed dictionary or native-speaker validation.

## Scope and results
- 500 kanji across five stages; 691 vocabulary entries; 500 sample sentences.
- 92 reading-review candidates: 10 in stage 1, 1 in stage 2, 9 in stage 3, 37 in stage 4, and 35 in stage 5.
- Cross-checked all 92 queue entries against their exact current kanji ID, vocabulary spelling, and hiragana reading. **0 stale or mismatched references**.
- The candidates were flagged because a source-matching step did not confirm them; **none is thereby proven incorrect**.
- No changes were made to kanji IDs, stored progress keys, or quiz state.

## Review priority
1. First validate stage 1 and 2 candidates (11 entries) against a licensed Japanese dictionary.
2. Review stage 3 (9 entries), then stage 4 (37) and stage 5 (35).
3. For each item, verify the exact word spelling, kana reading, part of speech, and common usage; document dictionary title, edition/URL, date, and license.
4. Check all 500 Japanese sentences and Korean translations for naturalness, conjugation, counters, politeness, and context.
5. Only after documented verification change `review_status` from `pending_editorial_dictionary_check` to a verified state. Never bulk-approve on intuition.

## Existing editorial corrections
- kanji-174: 終わる, kanji-194: 起こす
- kanji-373: 지구는 둥글습니다.
- kanji-500: 夫婦(ふうふ), replacing outdated occupational term 看護婦.

## Release gate
- Data remains `.draft.json`; dictionary cross-check, full native-language editorial pass, and source licensing are **pending**.
- No deployment or main-branch merge authorized by this report.

## Dictionary evidence batch 1 (2026-10-23)
- 5 of 92 review candidates have an exact reading verified with a published dictionary entry or kanji-reading index: 父(ちち), 母(はは), 分(ふん), 私(わたし), 円(えん). URLs and notes are stored in `READING-REVIEW-QUEUE.json` for each item.
- For 分, フン is documented as an on-reading; numeral combinations may surface ぷん. Do not replace the standalone entry with ぷん without context.
- 87 candidates remain `pending_editorial_dictionary_check`. Stage 1+2: 6 remaining, stages 3–5: 81 remaining.
- `dictionary_reading_checked` is **not** full word-sense, contextual usage, translation, licensing, or native-speaker approval.
