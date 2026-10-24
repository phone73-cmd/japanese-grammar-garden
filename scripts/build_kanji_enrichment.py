#!/usr/bin/env python3
"""Reproducible additive dictionary overlay. Requires mwparserfromhell.
python scripts/audit_korean_kanji.py SOURCES/kanjidic2.xml.gz
python scripts/build_kanji_enrichment.py SOURCES
Raw source downloads remain outside the published app. No progress data is read.
"""
from pathlib import Path
import sys,json,gzip,re,hashlib,xml.etree.ElementTree as ET,collections
import mwparserfromhell as mw
ROOT=Path(__file__).resolve().parents[1];D=Path(sys.argv[1]);OUT=ROOT/'data/kanji'
core=[x for n in range(1,6) for x in json.loads((OUT/f'kanji-stage-{n}-100.draft.json').read_text())['items']]+json.loads((OUT/'kanji-extra-125.draft.json').read_text())['items']
assert len(core)==len({x['id'] for x in core})==len({x['character'] for x in core})==625
audit=json.loads((OUT/'kanji-korean-readings.audit.json').read_text());audit={x['id']:x for x in audit['items']}
ktree=ET.parse(gzip.open(D/'kanjidic2.xml.gz'));kd={e.findtext('literal'):e for e in ktree.findall('character')};codes={(v.attrib['cp_type'],v.text):c for c,e in kd.items() for v in e.findall('codepoint/cp_value')}
pages={v['title']:v for f in sorted(D.glob('wikt-batch-*.json')) for v in json.loads(f.read_text())['query']['pages'].values()}
facts={x['character']:x for x in json.loads((OUT/'korean-gloss-exceptions.reviewed.json').read_text())['items']}
unicode_variants={}
japanese_old_forms={}
for line in (D/'Unihan_Variants.txt').read_text().splitlines():
 if line.startswith('#') or not line.strip():continue
 cp,kind,vals=line.split('\t')
 if kind=='kJapaneseOldVariant':japanese_old_forms[chr(int(cp[2:],16))]=[chr(int(v[2:],16)) for v in vals.split()]
 if kind in ['kJapaneseOldVariant','kTraditionalVariant','kSemanticVariant','kZVariant']:unicode_variants.setdefault(chr(int(cp[2:],16)),set()).update(chr(int(v.split('<')[0][2:],16)) for v in vals.split())
enpages={v['title']:v for v in json.loads((D/'en-wikt-exceptions.json').read_text())['query']['pages'].values()} if (D/'en-wikt-exceptions.json').exists() else {}
def text(p):return p.get('revisions',[{}])[0].get('slots',{}).get('main',{}).get('*','')
def clean(v):
 code=mw.parse(str(v))
 for t in reversed(code.filter_templates(recursive=True)):
  name=str(t.name).strip()
  if name in ['lang','언어'] and t.has('2'):code.replace(t,str(t.get('2').value))
  elif name in ['r','ruby'] and t.has('1') and t.has('2'):code.replace(t,str(t.get('1').value)+'/'+str(t.get('2').value))
 return re.sub(r'\s+',' ',code.strip_code()).strip()
def field(t,k):return clean(t.get(k).value) if t.has(k) else ''
def evidence(p,lang='ko'):
 rev=p['revisions'][0];return {'title':p['title'],'revision':rev['revid'],'timestamp':rev['timestamp'],'url':f'https://{lang}.wiktionary.org/w/index.php?title={p["title"]}&oldid={rev["revid"]}'}
def get_hun(p,lang='ko'):
 out=[]
 for t in mw.parse(text(p)).filter_templates():
  name=str(t.name).strip()
  if name not in ['한자풀이','ko-hanja','ko-hanjachar']:continue
  h=field(t,'훈' if name=='한자풀이' else '1');r=field(t,'음' if name=='한자풀이' else '2')
  if name=='한자풀이' and field(t,'음2'):
   first=re.search(r'^1\.\s*(.*?)\s*2\.',h)
   if first:h=first.group(1).strip(' ,')
   elif '(1.' in h:h=h.split('(1.')[0].strip(' ,')
   elif '('+r+')' in h:h=h.split('('+r+')')[0].strip(' ,')
   else:continue # Never assign a mixed unnumbered gloss to the wrong reading.
  if h and re.fullmatch(r'[가-힣]+',r) and not re.search(r'[{}<>]',h) and len(h)<50:out.append({'gloss':h,'reading':r,'source':evidence(p,lang)})
 return out
def variants(c):return list(dict.fromkeys(codes[(v.attrib['var_type'],v.text)] for v in kd[c].findall('misc/variant') if (v.attrib['var_type'],v.text) in codes))
def forms(p):
 out=[]
 for t in mw.parse(text(p)).filter_templates():
  if str(t.name).strip() in ['한자풀이','한자 낱말']:
   for key in ['정자','한국어']:
    v=field(t,key)
    if len(v)==1 and '\u3400'<=v<='\u9fff' and v!=p['title']:out.append({'character':v,'source':evidence(p)})
 return out
# Only explicit word / hiragana / Korean-gloss lines in the Japanese section.
word_candidates={}
for p in pages.values():
 sec=re.search(r'==\s*일본어\s*==([\s\S]*?)(?=\n==[^=]|\Z)',text(p))
 if not sec:continue
 for raw in sec.group(1).splitlines():
  line=clean(raw).strip('*:# ')
  match=re.match(r'^([一-龯ぁ-ゖァ-ヺー々]+)\s*/\s*([ぁ-ゖー]+)\s+([가-힣][^{}<>]*)$',line)
  if not match:continue
  word,reading,meaning=match.groups();meaning=meaning.strip(' .')
  if len(word)>8 or len(meaning)>36 or not meaning or any(v in meaning for v in ['(지명)','(성씨)','항목','참조','온요미','쿤요미']):continue
  word_candidates.setdefault((word,reading),{'word':word,'reading':reading,'meaning_ko':meaning,'source':evidence(p)})
authored={}
for line in (OUT/'extra-study-words.tsv').read_text().splitlines():
 word,reading,meaning=line.split('|');authored[word,reading]={'word':word,'reading':reading,'meaning_ko':meaning,'korean_translation_status':'authored-from-JMdict-English; expert-review-pending'}
requested=set(word_candidates)|set(authored)|{(w['word'],w['reading']) for x in core for w in x['example_words']};matched={pair:[] for pair in requested};english={pair:[] for pair in authored}
reading_forms={reading:set() for word,reading in requested}
for _,e in ET.iterparse(gzip.open(D/'JMdict_e.gz'),events=['end']):
 if e.tag!='entry':continue
 forms_={k.text for k in e.findall('k_ele/keb')}
 for r in e.findall('r_ele'):
  reading=r.findtext('reb');restricted={k.text for k in r.findall('re_restr')}
  if reading in reading_forms:reading_forms[reading].update(forms_ & restricted if restricted else forms_)
  for form in forms_:
   pair=(form,reading)
   if pair in matched and (not restricted or form in restricted):
    matched[pair].append(e.findtext('ent_seq'))
    if pair in english:
     for sense in e.findall('sense'):
      sk={z.text for z in sense.findall('stagk')};sr={z.text for z in sense.findall('stagr')}
      if (not sk or form in sk) and (not sr or reading in sr):english[pair].extend(g.text for g in sense.findall('gloss') if g.text)
 e.clear()
wordpool={}
for x in core:
 for w in x['example_words']:
  pair=w['word'],w['reading']
  if matched.get(pair):wordpool.setdefault(pair,{**w,'dictionary_entry_sequences':matched[pair],'dictionary_reading_match':True,'source_card_id':x['id']})
for pair,w in authored.items():
 if matched[pair]:wordpool.setdefault(pair,{**w,'dictionary_entry_sequences':matched[pair],'dictionary_reading_match':True,'english_source_glosses':list(dict.fromkeys(english[pair]))[:8]})
for pair,w in word_candidates.items():
 if matched[pair]:wordpool.setdefault(pair,{**w,'dictionary_entry_sequences':matched[pair],'dictionary_reading_match':True})
rows=[];exceptions=[]
for x in core:
 c=x['character'];a=audit[x['id']];e=kd[c];vs=variants(c);ps=[pages.get(v,{}) for v in [c]+vs]
 candidates=get_hun(ps[0]) or [g for p in ps[1:] for g in get_hun(p)]
 fact=facts.get(c)
 if fact:
  target=fact['korean_form'];assert target==c or target in unicode_variants.get(c,set()),(c,target)
  candidates=[{'gloss':fact['gloss'],'reading':fact['reading'],'source':fact['source']}]+candidates
 if not candidates and c in enpages:candidates=get_hun(enpages[c],'en')
 kr=a['korean_readings'];kr_source='KANJIDIC2'
 if not kr and candidates:kr=list(dict.fromkeys(g['reading'] for g in candidates));kr_source='Wiktionary'
 valid_gloss=[g for g in candidates if g['reading'] in kr]
 selected=[];seen=set()
 for w in x['example_words']+list(wordpool.values()):
  pair=w['word'],w['reading']
  if c in w['word'] and w['word'] not in seen and pair in wordpool and not (w.get('meaning_ko')=='공배' and w.get('source')):selected.append(wordpool[pair]);seen.add(w['word'])
  if len(selected)==3:break
 selected=[{**w,'connect_distractors_excluded':sorted({f[next(i for i,ch in enumerate(w['word']) if ch==c)] for f in reading_forms[w['reading']] if len(f)==len(w['word']) and all(ch==f[i] or ch==c for i,ch in enumerate(w['word'])) and len({f[i] for i,ch in enumerate(w['word']) if ch==c})==1 and f!=w['word']})} for w in selected]
 mappings=[v for p in ps[:1] for v in forms(p)]
 old_forms=japanese_old_forms.get(c,[])
 for v in old_forms:
  vp=pages.get(v,{})
  if get_hun(vp) and not mappings:mappings=[{'character':v,'source':evidence(vp),'relation':'Unicode-Japanese-old-form-and-Korean-hun-dictionary'}]
 if fact and fact['korean_form']!=c:mappings=[{'character':fact['korean_form'],'source':fact['source'],'relation':'Unicode-variant-and-Korean-dictionary-form'}]
 # A KANJIDIC variant is not automatically a Korean standard form.
 for v in vs:
  for back in forms(pages.get(v,{})):
   if back['character']==c and v!=c and get_hun(pages.get(v,{})) and not mappings:mappings=[{'character':v,'source':evidence(pages[v]),'relation':'dictionary-variant'}]
 kokuji=any('(kokuji)' in (m.text or '') for m in e.findall('reading_meaning/rmgroup/meaning'))
 status='source_matched' if valid_gloss else 'unconfirmed'
 row={'id':x['id'],'stage':x['stage'],'order':x['order'],'character':c,'korean_readings':kr,'korean_readings_source':kr_source,'korean_glosses':valid_gloss,'korean_gloss_status':status,'on':a['japanese_on_dictionary'],'kun':a['japanese_kun_dictionary'],'variants':vs,'japanese_old_forms':old_forms,'korean_forms':mappings,'kokuji':kokuji,'words':selected}
 rows.append(row)
 flags=[]
 if not valid_gloss:flags.append('한국식 훈 미확인')
 if not row['on']:flags.append('음독 사전 미수록 · 출제 제외')
 if not row['kun']:flags.append('훈독 사전 미수록 · 출제 제외')
 if any(g['reading'] not in kr for g in candidates):flags.append('불일치 한국 훈·음 원문 후보 제외')
 if kr_source!='KANJIDIC2':flags.append('KANJIDIC2 한국음 누락 · 별도 사전 연결')
 if candidates and not valid_gloss:flags.append('사전 간 한국음 불일치')
 if len(selected)<2:flags.append('대표 단어 2개 미만')
 if kokuji:flags.append('일본 고유 한자 · 한국음은 한국어 상용 여부와 구분')
 if len(kr)>1:flags.append('한국 한자음 복수')
 if flags:exceptions.append({'id':x['id'],'character':c,'flags':flags,'dictionary_korean':kr,'gloss_candidates':candidates})
meta={'schema':'jgg-kanji-enrichment-v1','version':'0.3.8-dev','total':625,'dictionary':{'url':'https://www.edrdg.org/kanjidic/kanjidic2.xml.gz','sha256':hashlib.sha256((D/'kanjidic2.xml.gz').read_bytes()).hexdigest(),'date':ktree.findtext('header/date_of_creation'),'database_version':ktree.findtext('header/database_version'),'licence':'CC BY-SA 4.0'},'word_dictionary':{'url':'https://www.edrdg.org/pub/Nihongo/JMdict_e.gz','sha256':hashlib.sha256((D/'JMdict_e.gz').read_bytes()).hexdigest()},'korean_gloss_source':'Wiktionary contributors (CC BY-SA 4.0); individual short factual lookups in Korean dictionaries for exceptions; per-record source links; source comparison is not expert certification','stats':{'dictionary_found':625,'korean_readings':sum(bool(r['korean_readings']) for r in rows),'korean_gloss_source_matched':sum(r['korean_gloss_status']=='source_matched' for r in rows),'two_or_more_words':sum(len(r['words'])>=2 for r in rows),'on_available':sum(bool(r['on']) for r in rows),'kun_available':sum(bool(r['kun']) for r in rows),'kokuji':sum(r['kokuji'] for r in rows)},'items':rows}
meta['unicode_source']={'url':'https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip','sha256':hashlib.sha256((D/'Unihan.zip').read_bytes()).hexdigest()}
meta['wiki_snapshot_hashes']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(D.glob('wikt-batch-*.json'))}
(OUT/'kanji-enrichment.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':'))+'\n')
(OUT/'KANJI-ENRICHMENT-EXCEPTIONS.json').write_text(json.dumps({'stats':meta['stats'],'items':exceptions},ensure_ascii=False,indent=2)+'\n')
report=['# 한자 625자 전수 대조 · v0.3.8-dev','','## 검증 범위','기존 625자 ID·단계·순서·단어·예문 파일을 변경하지 않고 연결 데이터를 생성합니다.','KANJIDIC2 공식 자료의 korean_h·ja_on·ja_kun을 전수 대조했습니다.','한국식 훈은 위키낱말사전의 명시적인 훈·음 필드와 예외 항목의 한국 한자 사전 개별 조회를 사용합니다. 잘못된 필드는 그대로 채택하지 않습니다. 짧은 훈·음 사실 정보 외에 사전의 긴 정의·예문·미디어는 복제하지 않았습니다. 사전 간 대조·출처 연결이며, 공인 기관 인증 및 전문가 전체 교차 감수 완료를 의미하지 않습니다.','미확인 값은 빈 목록으로 유지하고 출제하지 않습니다.','KANJIDIC2의 이체자 관계는 한국 정자체 확정과 구별합니다. 한국 표기 관계는 별도 명시 출처가 있는 경우만 표시합니다.','','## 집계',*[f'- {k}: {v}' for k,v in meta['stats'].items()],'','## 예외 및 남은 작업','| ID | 한자 | 검토 항목 |','|---|---|---|',*[f'| {r["id"]} | {r["character"]} | {"; ".join(r["flags"])} |' for r in exceptions],'','## 재현','1. 공식 KANJIDIC2 및 JMdict_e 압축 파일, 위키낱말사전 API revision 스냅샷을 확보합니다.','2. `python scripts/audit_korean_kanji.py SOURCES/kanjidic2.xml.gz`','3. `pip install -r scripts/requirements-kanji-audit.txt`','4. `python scripts/build_kanji_enrichment.py SOURCES`','원문 압축 파일 SHA-256, 사전 날짜, 문서별 revision·고유 링크는 결과 JSON에 기록합니다.','한국어 뜻이 있는 기존 단어 및 위키낱말사전 일본어 파생어, JMdict 영어 의미에 근거해 작성한 한국어 번역을 사용합니다. 모든 추가 표기/읽기를 JMdict 제한 조건까지 확인하며 원어민 전체 번역 감수는 미완료입니다. 기존 단어 번역은 이전 편집 상태를 유지합니다.','대표 단어가 2개 미만인 글자는 검증되지 않은 단어로 채우지 않습니다.','','## 이용 조건','EDRDG KANJIDIC2/JMdict 및 위키낱말사전 파생 데이터는 CC BY-SA 4.0으로 배포합니다. 예외 한자 사전은 짧은 훈·음 사실 정보 조회 근거를 링크했으며 해당 사전의 긴 정의문·이미지는 사용하지 않습니다. Unicode 자료는 Unicode 이용 조건과 출처를 고지합니다. 출처 링크 및 변경 사실을 앱 자료 출처 화면에 표시합니다. SKIP 코드는 사용하지 않습니다.']
(OUT/'KANJI-ENRICHMENT-AUDIT.md').write_text('\n'.join(report)+'\n')
print(json.dumps(meta['stats'],ensure_ascii=False));print('attested additional word candidates',sum(bool(matched[p]) for p in word_candidates));print('missing gloss',''.join(r['character'] for r in rows if not r['korean_glosses']));print('short words',''.join(r['character'] for r in rows if len(r['words'])<2))
print('unmatched authored words',[p for p in authored if not matched[p]])
(OUT/'STUDY-WORDS-TRANSLATION-REVIEW.json').write_text(json.dumps({'note':'Korean translations authored from the attached JMdict English glosses; native expert review pending. Exact Japanese spelling/reading verified including re_restr and sense restrictions.','words':[{**w,'english_source_glosses':list(dict.fromkeys(english[pair])),'dictionary_entry_sequences':matched[pair]} for pair,w in authored.items()]},ensure_ascii=False,indent=2)+'\n')
