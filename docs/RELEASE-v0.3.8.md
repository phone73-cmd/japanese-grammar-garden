# v0.3.8-dev 한자 625자 적용·검증 기록

기준일: 2026-10-24 (한국 시간)

## 기준·통합 이력

- 저장소: https://github.com/phone73-cmd/japanese-grammar-garden
- 시작 main: e6b84121e4d10a7f4f08369f4dba5395ca99d469 (v0.3.7-dev)
- 검증 브랜치: feature/kanji-korean-readings-audit
- 검증 스크립트 시작: c35141e6aba99d6959b75b05d630558cf18baae0
- 데이터·기능 통합: 1275a7533166bb3e1b1ec27b220e06b883148230 (검증 브랜치 이력을 추가 부모로 연결)
- 402px 연결 문제 화면 보완: 04eec92401f78700c019bc58b3c2dd11c7edc38b
- 앱: https://phone73-cmd.github.io/japanese-grammar-garden/

## 전수 대조

| 항목 | 결과 |
|---|---:|
| 기존 ID·글자 중복/누락 | 0 |
| 공식 KANJIDIC2 수록 | 625/625 |
| 한국 한자음 연결 | 625/625 |
| 한국식 훈 출처 대조 | 625/625 |
| 대표 단어 2~3개 | 625/625 |
| 음독 수록 | 624/625 |
| 훈독 수록 | 561/625 |
| Unicode 일본 구자체 관계 | 95자 |
| 한국 사전 표기 비교 근거 | 83자 |
| 일본 고유 한자 표시 | 働·込 |

공식 KANJIDIC2 2026-10-24 자료를 사용했습니다. 한국음 624자는 KANJIDIC2에 있으며, 누락된 収는 별도 사전으로 확인했습니다. 込의 음독 및 64자의 훈독은 사전에 없으므로 임의 생성하거나 해당 유형에서 출제하지 않습니다.

한국식 훈의 '출처 대조'는 해당 사전 필드와 일치함을 뜻합니다. 공인 기관 인증이나 전문가 전체 감수 완료를 뜻하지 않습니다. 위키낱말사전과 예외 항목의 개별 한국 한자사전 조회를 사용하며, 모호하거나 잘못 결합된 훈·음 후보는 제외했습니다. 일본 구자체나 사전 이체자를 한국 표준자로 일괄 간주하지 않습니다.

[전수 대조](../data/kanji/KANJI-ENRICHMENT-AUDIT.md) · [예외 목록](../data/kanji/KANJI-ENRICHMENT-EXCEPTIONS.json) · [번역 감수 목록](../data/kanji/STUDY-WORDS-TRANSLATION-REVIEW.json)

## 적용 내용

- 기존 뜻·발음 펼침 영역에 한국식 훈·음, 한국 한자음, 음독+히라가나, 훈독, 표기 비교 추가.
- 단어별 듣기: 사전 히라가나, ja-JP, rate 0.85. 기존 일본어 음성 엔진 정책 유지.
- 기존 단어 읽기·뜻 + 한국음·음독·훈독·단어 빈칸 한자 연결의 6유형을 10문제 시험에 혼합.
- 帰る/返る/還る처럼 같은 읽기로 성립하는 대체 표기를 연결 문제 오답에서 제외.
- 새 오답은 유형과 문제 원본을 추가 필드로 저장. 다른 유형의 정답으로 오답이 잘못 지워지지 않으며, 저장된 선지로 이어 풀기.
- 기존 복습 일정·점수·시도 기록·JSON schema 1 백업·IndexedDB 보호 사본 유지.
- 연결 문제는 빈칸 단어·발음·뜻을 서로 다른 줄과 크기로 표시.

## 검증 결과

- node tests/stabilization.cjs: 35개 통과. Node DOM·저장소·서비스워커 하네스이며 실제 iPhone 테스트는 아닙니다.
- 625개 카드, 원본 단어·예문 불변, 6유형, 6단계 완료, 백업 복구, 이전 백업 구조, 유형별 오답 해결, 일본어 음성 인자, 동음 대체 표기 제외 검사.
- Chrome의 402 × 874 CSS px iframe에서 카드·가로 넘침·44px 단어 듣기 버튼·라이트/다크·6유형 화면 확인. 데스크톱 스크롤바로 내용 폭 387px인 경우도 포함.
- v0.3.7의 三つ 1/10 선택 답안을 저장한 상태로 업데이트하여 문제·답안 보존 확인.
- 실제 앱 주소에서 연결 문제 6/10을 새로고침하여 진행·답안 보존 확인. 브라우저 뒤로가기 시 앱 내부 중단 확인창과 취소 확인.
- 다크모드 본문 RGB(243,239,250), 출처 링크 RGB(196,180,242), 카드 배경 RGB(34,33,39) 확인.
- 필수 캐시 37개 존재. 새 연결 데이터·라이선스 사본 포함. Node 오프라인 요청 검사 통과.
- Pages 작업 40070618013 및 화면 보완 작업 40071273913 성공.
- 공개 index.html·한자 JS·서비스워커·연결 데이터와 로컬 파일 일치 확인.

## 원본 보호

기존 원본 6개 파일의 Git blob SHA가 시작 main과 모두 같습니다.

| 파일 | Git blob SHA |
|---|---|
| data/kanji/kanji-extra-125.draft.json | 9037094c4bb2e21c62abe4a9122d0a13e4a4b989 |
| data/kanji/kanji-stage-1-100.draft.json | 3623bc62a46b0befb1a19dfce279d1938f3ce814 |
| data/kanji/kanji-stage-2-100.draft.json | 497b7b1469afb7e1f0670f8bec4ecbfb719dad47 |
| data/kanji/kanji-stage-3-100.draft.json | ecc698ce954216f3703f707d66d0a20f4978fec1 |
| data/kanji/kanji-stage-4-100.draft.json | 6a17aa7ed3220220d76b47618263a45615256d8c |
| data/kanji/kanji-stage-5-100.draft.json | 863ff3ab96c37fb618de68ed9bd418e904703a96 |

저장 키 jgg.progress.v1, jgg.session.v1, jgg.session.backup.v1, jgg.kanji.v1, jgg.kanji.quiz.v1, jgg.kanji.quiz.backup.v1 변경·초기화·마이그레이션 없음.

## 수정·추가 파일

- index.html
- kanji-app.js
- kanji-app.css
- service-worker.js
- sources.html
- README.md
- tests/stabilization.cjs
- scripts/audit_korean_kanji.py
- scripts/build_kanji_enrichment.py
- scripts/fetch_kanji_sources.py
- scripts/requirements-kanji-audit.txt
- data/kanji/kanji-enrichment.json
- data/kanji/kanji-korean-readings.audit.json
- data/kanji/KOREAN-READINGS-AUDIT.md
- data/kanji/KANJI-ENRICHMENT-AUDIT.md
- data/kanji/KANJI-ENRICHMENT-EXCEPTIONS.json
- data/kanji/korean-gloss-exceptions.reviewed.json
- data/kanji/extra-study-words.tsv
- data/kanji/STUDY-WORDS-TRANSLATION-REVIEW.json
- data/kanji/QA-STATUS.md
- docs/licenses/UNICODE.txt
- docs/licenses/EDRDG.html
- docs/RELEASE-v0.3.8.md (이 기록)

## 미확인·남은 감수

- 실제 iPhone 16 Pro Safari·홈 화면 PWA의 안전 영역·스와이프·당겨 새로고침·비행기 모드·업데이트 후 기록 보존: 미확인.
- 실제 기기의 일본어 음성 종류·음질·청취 결과: 미확인. 호출 코드와 버튼 연결 검사만 수행.
- 전체 한국식 훈의 공인 사전 추가 교차 감수 및 언어 전문가 정밀 감수: 미완료.
- 전체 대표 단어 한국어 번역·예문의 원어민 정밀 감수: 미완료. 출처와 검수 목록 유지.
- 기존 모으기의 홈 화면 추가용 '펼친 책+벚꽃' 앱 아이콘 변경안은 이번 한자 작업에 적용하지 않고 유지합니다.
