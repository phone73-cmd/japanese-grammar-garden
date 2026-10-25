# 콘텐츠 출처·검수 범위 — v0.3.0-dev

- 일본어 문법정원 자체 집필: 57개 추가 단원 설명, 예문, 한국어 번역, 퀴즈와 조립 연습. 기존 1·6·7과의 30개 문항 인덱스 유지.
- 문법 체계 참고: Japan Foundation, [Irodori resources](https://www.irodori.jpf.go.jp/en/resources.html). 교재의 설명·문제·이미지를 복사하지 않았으며 이 앱의 수업은 독립 초안입니다. 공식 교육과정 또는 JLPT 급수 인증 자료가 아닙니다.
- 기존 한자·어휘 초안: [OpenJLPT](https://github.com/evanclan/OpenJLPT), CC BY-SA 4.0. [upstream NOTICE](https://github.com/evanclan/OpenJLPT/blob/main/NOTICE.md)와 LICENSE 확인(2026-10-23).
- OpenJLPT가 고지한 상위 출처: JMdict/KANJIDIC2 — James William Breen 및 Electronic Dictionary Research and Development Group; Jonathan Waller의 비공식 JLPT 목록; Tatoeba. 현재 자체 집필 예문을 외부 문장 검증 완료 자료로 표시하지 않습니다. KanjiVG 그림은 포함하지 않습니다.
- 공식 읽기 대조: [JMdict_e.gz](https://www.edrdg.org/pub/Nihongo/JMdict_e.gz), [EDRDG 프로젝트](https://www.edrdg.org/wiki/JMdict-EDICT_Dictionary_Project.html), [EDRDG 이용 조건](https://www.edrdg.org/edrdg/licence.html). 파일 SHA-256와 entry_sequence는 DICTIONARY-CHECK-v0.3.0.json과 READING-REVIEW-QUEUE.json 참조.
- 92/92 후보 및 691/691 단어 항목의 표기·읽기를 re_restr 제한을 고려해 정확히 대조했습니다. 뜻·예문 전체를 사전이 보증한다는 뜻은 아닙니다. 원어민·독립 전문가 감수는 미완료입니다.
- 한자 500개 예문은 AI 편집 1차 점검을 기록하고 7건을 수정했습니다. 단어와 예문의 연결 및 다의적 읽기 검토 기록은 SENTENCE-REVIEW-v0.3.0.json 참조. 모든 데이터는 .draft.json 상태입니다.

## 데이터 이용 고지

수정·번역·선정한 한자 파생 데이터는 **CC BY-SA 4.0**으로 제공합니다. 출처와 기존 권리자 표기를 유지하며 수정 사실을 알립니다. [라이선스 링크](https://creativecommons.org/licenses/by-sa/4.0/). 원자료와 편집 초안은 정확성 보증 없이 제공됩니다. 이 고지는 앱 코드 전체의 라이선스를 변경하지 않습니다.

사전 대조 파일은 검증 시점의 스냅샷입니다. 정식 콘텐츠 승격 전과 자료 갱신 시 같은 대조 스크립트를 다시 실행하고 근거 파일 해시를 갱신해야 합니다. 원자료별 특이 조건의 법률 전문가 검토를 완료했다고 주장하지 않습니다.

## v0.3.5-dev 추가 한자

기존 문법·한자 예문에 있는 미수록 125자를 별도 카드로 추가했다. 예문은 기존 자체 편집 자료를 재사용하고 한국어 단일 글자 뜻·대표 단어 뜻은 별도로 편집했다. 대표 단어 125항목(중복 단어 포함)의 표기·읽기는 공식 JMdict XML의 re_restr를 고려해 정확 대조했으며 각 항목에 entry_sequence를 기록했다. 데이터는 기존 한자 파생 데이터와 동일한 CC BY-SA 4.0 고지를 따른다. 사전의 뜻풀이를 복제하지 않았으며 읽기 대조를 뜻·예문 전체 검수로 간주하지 않는다. 상세 해시 및 재생성 명령은 data/kanji/EXTRA-KANJI-STATUS.md 참조.


## v0.3.9-dev 학습 보강

기존 600문제 인덱스 보존, 830문제 추가. 설명·활용표·9개 역할 대화는 자체 작성했습니다. TUFS 문법 모듈 https://www.coelang.tufs.ac.jp/mt/ja/gmod/steplist.html 및 이로도리 https://www.irodori.jpf.go.jp/resources.html 의 체계를 참고했으며 교재 문장·미디어를 복제하지 않았습니다. 구조 검사와 원어민 감수는 다르며 전체 원어민 감수는 미완료입니다. 세부 결과는 RELEASE-v0.3.9.md 및 data/grammar/COURSE-AUDIT-v0.3.9.json에 기록합니다.


## v0.3.10-dev 예문·평가 자료

practice-data.js는 scripts/build_practice.py의 자체 작성 문형·명시적인 읽기·한국어 활용 표에서 생성합니다. 문형 기능 대조와 어휘 변형을 포함합니다. 학습 예문과 평가 전용 문장을 구분하며, 전체 원어민 정밀 감수는 미완료입니다. 외부 교재 문장·음원은 복제하지 않았습니다. 수량·반복 회피·보존 결과는 RELEASE-v0.3.10.md와 PRACTICE-AUDIT-v0.3.10.json을 참조하세요.


## v0.3.11-dev 사전·검색·분류

추가 14자는 KANJIDIC2 2026-10-24 스냅샷과 한국어 위키낱말사전의 글자별 revision을 대조했습니다. 届/滞는 정자 屆/滯의 한국식 훈을 연결하고 공식 이체자 정보를 비교합니다. 단어 29개는 JMdict 표기·읽기·sense 제한을 대조했으며 한국어 번역은 자체 작성 초안입니다. 원어민 정밀 감수는 미완료입니다. 원본 625자 자료는 수정하지 않았습니다.

검색 단어의 품사는 JMdict의 해당 표기/읽기 제한을 적용한 sense POS에서 가져옵니다. 기능어·문형·의문사 등은 명시적인 학습용 분류이며, 불명확한 5항목은 분류를 추측하지 않습니다. 연결 JSON과 검색 JSON의 사전 파생 부분은 EDRDG/위키낱말사전 CC BY-SA 4.0 출처·조건을 따릅니다. 기존 sources.html 및 docs/licenses/EDRDG.html, UNICODE.txt를 유지합니다.

## v0.3.13-dev 정확도 보강

위 v0.3.11의 미분류 5항목은 v0.3.12에서 수사·연체사로 연결해 현재 0개입니다. v0.3.13은 『いろどり』 입문 18과의 に/へ, 국제교류기금 Vたことがあります의 경험 문맥, 문화청 謙譲語I 설명을 근거로 기존 자체 작성 자료를 편집했습니다. 출처는 [검수 보고서](ACCURACY-REVIEW-v0.3.12.md)에 기록했습니다. 교정 문장은 자체 작성이며 전체 원어민 감수 완료를 뜻하지 않습니다.
