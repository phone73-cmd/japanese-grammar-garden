# v0.3.9-dev — 전체 60단원 학습 보강

기준일: 2026-10-24 (한국 시간). 기준 main: 7ee305520aa756212df4c86fe21b9e855b67ba8b.

## 반영 내용

- 기존 60단원과 600문제의 단원 ID·문제 인덱스·내용을 보존하고 830문제를 추가했습니다. 전체 1,430문제 중 120개는 별도의 OX 판단 항목입니다. 일반 시험은 10문제를 선택하며 OX 판단 항목은 일반 시험 선택 대상에서 제외합니다.
- 히라가나 기본 46자, 탁음·반탁음 25자 및 주요 요음 33개; 가타카나 기본 46자, 탁음·반탁음 25자·요음 33개·외래어 조합 23개. 문자·조합 총 231개, 각각 정방향·역방향 문제를 제공합니다. 기본 문자표는 や행·わ행의 빈칸을 유지하고 요음은 3열입니다. 역사적 ゐ・ゑ 등과 모든 희귀 조합을 포함한 목록은 아닙니다.
- 문자 듣기와 문자별 정답 기록을 구분합니다. 같은 소리의 じ/ぢ·ず/づ는 역방향 정답 선택지에서 서로 오답으로 사용하지 않습니다. ぬ/め, シ/ツ 등 모양이 비슷한 글자를 우선 비교합니다.
- 54개 일반 단원에 핵심 정리·비교 표·주의사항을 추가했습니다. た형은 26과에서 て형과 연결하고 39·45과에서 재확인하며, 47과에서 보통형의 시제·부정 체계를 설명합니다. 선행 단원 이동 버튼을 제공합니다.
- 6개 종합평가 단원은 앞선 9개 단원에서 최소 한 문제씩 출제합니다. 미학습·오답·복습 예정과 문제 유형을 함께 고려합니다. 기존의 종합평가 고정 10문제도 인덱스를 유지하여 과거 오답 복습이 가능합니다.
- 여행 51~59과에 역할별 대화 9개·36개 발화를 추가했습니다. 각 발화에 히라가나·한국어 뜻·일본어 음성을 제공합니다. 새 발화는 기존 예문 배열에 삽입하지 않으므로 예전 예문 번호도 바뀌지 않습니다.
- 문장 조립은 각 단원의 기존 예문 3~4개를 연속 연습합니다. 첫 예문은 기존 수동 조각, 나머지는 Intl.Segmenter로 분리하며 미지원 환경은 글자 조각을 사용합니다. 진행 중 조각·답안·문장 순서를 저장하고 예전 한 문장 세션도 복원합니다.
- 학습 확인 체크·문자 듣기/정답 진도·단원 시험 성적을 분리하고 ‘완료’를 ‘시험 통과’로 변경했습니다. 기존 최고 점수는 변경하지 않습니다. 결과 화면에는 오답 단원·유형별 복습 안내 및 ‘학습 다시 보기’ 책 아이콘을 넣었습니다.
- 홈 화면 앱 아이콘은 라벤더 불투명 배경·민트 표지의 아이보리 책·분홍 벚꽃입니다. iOS 180px, PWA 192/512px PNG에 반영했습니다. 기존 설치 아이콘이 바뀌는 시점은 OS 캐시 정책에 영향을 받으며 실기기 설치 결과는 미확인입니다.

## 기록 및 데이터 보존

6개 원본 한자 JSON과 기존 kanji-enrichment.json, grammar-lessons.js, sentence-parts.js는 수정하지 않았습니다. 기존 문법 600문제의 SHA-256을 tests/fixtures/legacy-questions-v038.sha256.json으로 비교합니다.

저장 키 jgg.progress.v1, jgg.session.v1, jgg.session.backup.v1, jgg.kanji.v1, jgg.kanji.quiz.v1, jgg.kanji.quiz.backup.v1 및 IndexedDB 저장소는 유지합니다. 문법 기록에 courseProgress·kanaProgress만 추가하며 기존 schema 1 백업·복원에 포함합니다. 예전 백업에는 두 항목이 없어도 복원할 수 있습니다. 자동 초기화·이전 기록 삭제는 하지 않습니다.

## 검증

- node scripts/audit_course.cjs: 전체 1,430문제 선택지·정답·해설 구조, 기존 600문제 SHA, 46자 전체 및 동음 글자 오답 제외 통과.
- node tests/stabilization.cjs: 44개 검사 통과. 기존 35개 기능의 변경된 문제 수·여러 문장 조건을 반영하고 세션 복구·균형 출제·추가 진도·음성·과거 세션 호환 9개 검사를 추가했습니다. Node DOM/storage/SW 모의 검사이며 실제 브라우저 검사와 구분합니다.
- python scripts/audit_kanji_followup.py SOURCE/kanjidic2.xml.gz: 625자 공식 사전 재대조, 음독·훈독·수록 한국음 불일치 0. 한국식 훈의 읽기와 연결 한국음 차이 후보 0, 동일 표기·읽기의 번역 불일치 후보 0. 収는 기존 별도 출처를 유지합니다. 이는 의미·문맥의 전문가 감수 완료를 뜻하지 않습니다.
- SW jgg-v0.3.9-dev-ui3, 필수 캐시 40개. 새 과목 데이터·런타임·CSS를 한 캐시로 설치하고 사용자 업데이트 적용 방식을 유지합니다.
- 실제 GitHub Pages v0.3.9-dev 갱신 및 첫 배포 workflow 40093685651 성공 확인.
- Chrome 402×874 iframe: 기본 문자 46개, 최소 버튼 약 60.6×76px, 페이지 client/scroll 387/387px(iframe 402px에서 데스크톱 스크롤바 제외), 활용표·선행 버튼 331/331px로 가로 넘침 없음. 호텔 대화 4개 발화 표시 확인.
- 기존 v0.3.8-dev ‘く’ 1/10 문제의 D. ku 답안이 v0.3.9-dev 새로고침·명시적인 업데이트 적용 이후에도 유지됨을 실제 브라우저에서 확인.
- 문장 조립 1/4 정답→2/4 이동, 새 탭 2/4 복원, パン 조각 선택 후 직접 앱 새로고침에도 선택 유지 확인.
- 추가 발견·수정: 학습 체크 직후 진도 숫자 즉시 갱신, 문자 듣기 후 포커스 유지, 분리된 활용 어미를 문장 조각에 병합. 새 탭에서 복구된 퀴즈에 내부 이전 경로를 만들어 브라우저 뒤로가기 앱 확인창을 보장하는 코드 및 자동 검사 추가. 이력 가드가 있는 재새로고침에서는 중복 가드를 만들지 않습니다.
- 대화 듣기 버튼의 실제 측정에서 35px/줄바꿈을 발견하여 76×44px 고정, 예문 듣기도 최소 44px로 보완했습니다.
- 최종 UI 패치 workflow 40094305885 성공. index/course-data/course-runtime/CSS/SW/manifest와 세 PNG 아이콘의 실제 Pages 응답이 로컬 수정본과 SHA-256 일치.
- 최종 실제 브라우저 재확인: 핵심 학습 체크 즉시 1/5로 갱신; 새 탭에서 복구된 2/4 조립 퀴즈의 브라우저 뒤로가기에서 앱 확인창 표시, 취소 후 선택 조각 유지; 다크 모달 배경 rgb(34,33,39), 글자 rgb(243,239,250); 대화 듣기 4개 버튼 모두 76×44px. 기기 설정 테마로 복원.
- schema 1 JSON 실제 가져오기 핸들러를 통한 새 진도 round-trip 및 새 필드 없는 구 백업 호환 검사 추가. 총 44개 자동 검사 통과.

## 배포 확인

기능 커밋 11a5d79c963e9bc5aadfb4614f7c3ef2b955f74c, 복구·진도 수정 83a7ab3a30168c4440a65e153fbfc2b9efe9eebf, 최종 UI 수정 580eaf6f7b3b97a3ce445c91b805e5f3c89924d3. 세 GitHub Pages workflow 모두 success. 앱 URL https://phone73-cmd.github.io/japanese-grammar-garden/ . 최종 테스트·보고서 문서 커밋은 위 기능 커밋 이후 추가합니다. 원본 자료를 초기화하지 않았습니다.

## 언어 검수 범위와 남은 작업

- 설명·문제·대화는 자체 작성했습니다. TUFS 문법 모듈과 국제교류기금 이로도리의 학습 체계를 참고하며 교재 문장·그림·음원을 복제하지 않았습니다. 모든 개별 새 문제를 공식 기관이 승인한 것은 아닙니다.
- 한자 한국식 훈 625자의 공인 사전 추가 교차 감수, 전체 예문·한국어 번역 및 새 문법 콘텐츠의 원어민 정밀 감수는 미완료입니다. 기존 초안 상태를 유지합니다. 추가 회화·표에 나오는 한자가 기존 625자에 없으면 한자 카드 연결 대상이 아닙니다. 기존 125자 추가 목록의 범위는 기존 예문 기준입니다.
- 실제 iPhone 16 Pro Safari/PWA의 스와이프 뒤로가기·안전 영역·오프라인 실행·업데이트·음성 품질·홈 화면 아이콘 설치 결과는 미확인입니다.

## 수정 파일

index.html, course-data.js, course-runtime.js, course.css, kanji-app.js, service-worker.js, manifest.webmanifest, icons/apple-touch-icon.png, icons/icon-192.png, icons/icon-512.png, scripts/build_course.py, scripts/audit_course.cjs, scripts/audit_kanji_followup.py, tests/stabilization.cjs, tests/fixtures/legacy-questions-v038.sha256.json, data/grammar/COURSE-AUDIT-v0.3.9.json, data/grammar/CONTENT-STATUS.json, data/kanji/FOLLOWUP-AUDIT-v0.3.9.json, data/kanji/QA-STATUS.md, README.md, sources.html, docs/CONTENT-SOURCES.md, docs/RELEASE-v0.3.9.md.

## 앱 아이콘 제작 기록

imagegen 스킬의 기본 내장 도구 사용. 최종 파일 icons/apple-touch-icon.png, icons/icon-192.png, icons/icon-512.png. 생성 원본은 정사각형 불투명 PNG이며 아래 요청으로 제작 후 크기만 변환했습니다.

> iOS home screen app icon for Japanese Grammar Garden. Soft pastel 3D clay illustration, opaque lavender full-bleed background, centered open ivory book with mint green covers and blank curved pages, small five-petal pink cherry blossom upper right. Soft rounded forms, subtle shadows, legible silhouette, safe margins. No words, letters, watermark, frame, transparency or baked-in rounded outer corners.
