"""Append the fourteen unlinked study-text kanji; never rewrites the original 625.
Usage: python scripts/build_kanji14.py /path/to/dictionaries
"""
import sys,json,re,gzip,hashlib,ast,xml.etree.ElementTree as ET
from pathlib import Path
import mwparserfromhell as mw
ROOT=Path(__file__).resolve().parents[1];D=Path(sys.argv[1]);OUT=ROOT/'data/kanji'
funcs=ast.parse((ROOT/'scripts/build_kanji_enrichment.py').read_text());exec(compile(ast.Module(body=[n for n in funcs.body if isinstance(n,ast.FunctionDef) and n.name in ['text','clean','field','evidence','get_hun']],type_ignores=[]),'source-parser','exec'))
kd={e.findtext('literal'):e for e in ET.parse(gzip.open(D/'kanjidic2.xml.gz')).findall('character')}
pages={v['title']:v for v in json.loads((D/'wikt-new14.json').read_text())['query']['pages'].values()}
raw='''並|並ぶ/ならぶ/줄을 서다;並列/へいれつ/병렬
券|航空券/こうくうけん/항공권;入場券/にゅうじょうけん/입장권
召|召す/めす/드시다;召集/しょうしゅう/소집
届|届ける/とどける/배달하다;届く/とどく/도착하다
探|探す/さがす/찾다;探検/たんけん/탐험
滞|滞在/たいざい/체류;渋滞/じゅうたい/교통 정체
看|看護/かんご/간호;看板/かんばん/간판
航|航空/こうくう/항공;航海/こうかい/항해
袋|袋/ふくろ/봉지;手袋/てぶくろ/장갑
許|許可/きょか/허가;免許/めんきょ/면허
護|保護/ほご/보호;看護/かんご/간호
販|販売/はんばい/판매;自動販売機/じどうはんばいき/자동판매기
軽|軽い/かるい/가볍다;軽食/けいしょく/가벼운 식사
辛|辛い/からい/맵다;辛い/つらい/괴롭다;香辛料/こうしんりょう/향신료'''
words={ch:[dict(zip(['word','reading','meaning_ko'],v.split('/'))) for v in s.split(';')] for ch,s in (l.split('|') for l in raw.splitlines())}
requested={(w['word'],w['reading']) for rows in words.values() for w in rows};matches={p:[] for p in requested};gloss={p:[] for p in requested};same={r:set() for _,r in requested}
for _,e in ET.iterparse(gzip.open(D/'JMdict_e.gz'),events=['end']):
 if e.tag!='entry':continue
 forms={x.text for x in e.findall('k_ele/keb')}
 for r in e.findall('r_ele'):
  reading=r.findtext('reb');restricted={x.text for x in r.findall('re_restr')};allowed=forms&restricted if restricted else forms
  if reading in same:same[reading].update(allowed)
  for form in allowed:
   pair=form,reading
   if pair not in requested:continue
   matches[pair].append(e.findtext('ent_seq'))
   for sense in e.findall('sense'):
    sk={x.text for x in sense.findall('stagk')};sr={x.text for x in sense.findall('stagr')}
    if (not sk or form in sk) and (not sr or reading in sr):gloss[pair].extend(x.text for x in sense.findall('gloss') if x.text)
 e.clear()
assert all(matches.values()),[k for k,v in matches.items() if not v]
loadjs=lambda f,n:json.loads((ROOT/f).read_text().split(n+'=')[1].strip().rstrip(';'))
p=loadjs('practice-data.js','window.JGG_PRACTICE_DATA');c=loadjs('course-data.js','window.JGG_COURSE_DATA');g=loadjs('grammar-lessons.js','window.JGG_LESSONS')
sentences=[]
for id,d in g.items():sentences += [dict(ja=e[0],reading=e[1],translation_ko=e[3],source='grammar-'+id) for e in d['examples']]
for id,d in p['lessons'].items():
 sentences += [dict(ja=e[0],reading=e[1],translation_ko=e[3],source='practice-'+id) for e in d['examples']]
 sentences += [dict(ja=r[1],reading=r[2],translation_ko=r[4],source='dialogue-'+id) for rows in d.get('dialogues',[]) for r in rows]
for id,d in c['lessons'].items():sentences += [dict(ja=r[1],reading=r[2],translation_ko=r[3],source='dialogue-'+id) for r in d.get('dialogue',[])]
known={x['character'] for f in [*(OUT.glob('kanji-stage-*-100.draft.json')),OUT/'kanji-extra-125.draft.json'] for x in json.loads(f.read_text())['items']}
missing=set(re.findall('[一-龯]',''.join(x['ja'] for x in sentences)))-known;assert missing==set(words),(missing,set(words))
oldforms={}
for line in (D/'Unihan_Variants.txt').read_text().splitlines():
 if not line or line.startswith('#'):continue
 cp,typ,vs=line.split('\t')
 if typ=='kJapaneseOldVariant':oldforms[chr(int(cp[2:],16))]=[chr(int(v[2:],16)) for v in vs.split()]
# These are sourced Korean traditional counterparts; Japanese form stays the card glyph.
traditional={'並':'竝','届':'屆','滞':'滯','軽':'輕'}
items=[];overlay=[]
for offset,ch in enumerate(sorted(words),126):
 e=kd[ch];read=lambda typ:list(dict.fromkeys(r.text for r in e.findall('./reading_meaning/rmgroup/reading') if r.attrib.get('r_type')==typ and r.text))
 hun=get_hun(pages[traditional.get(ch,ch)] if ch in ['届','滞'] else pages[ch]);assert hun,(ch,'missing source hun')
 assert all(x['reading'] in read('korean_h') for x in hun),(ch,hun)
 wordlist=[]
 for w in words[ch]:
  pair=w['word'],w['reading'];wordlist.append({**w,'dictionary_reading_match':True,'dictionary_entry_sequences':matches[pair],'source_reading_match':True,'meaning_en_evidence':list(dict.fromkeys(gloss[pair]))[:8],'gloss_status':'authored_translation_source_matched_native_review_pending','connect_distractors_excluded':sorted({form[next(i for i,c in enumerate(w['word']) if c==ch)] for form in same[w['reading']] if len(form)==len(w['word']) and form!=w['word'] and all(a==b for a,b in zip(form,w['word']) if b!=ch) and len({a for a,b in zip(form,w['word']) if b==ch})==1})})
 item=dict(id='extra-'+format(ord(ch),'x'),character=ch,stage=6,order=offset,group_name='문장 속 추가 한자',meaning_ko=hun[0]['gloss'],on_readings=read('ja_on'),kun_readings=read('ja_kun'),example_words=wordlist,example_sentence=next(s for s in sentences if ch in s['ja']),editorial_status='draft_source_matched',source='existing-study-texts-and-dictionary-evidence')
 items.append(item)
 forms=[dict(character=traditional[ch],source=hun[0]['source'])] if ch in traditional else []
 overlay.append(dict(id=item['id'],character=ch,stage=6,order=offset,korean_readings=read('korean_h'),korean_readings_source='KANJIDIC2',korean_glosses=hun,korean_gloss_status='source_matched',on=read('ja_on'),kun=read('ja_kun'),variants=oldforms.get(ch,[]),japanese_old_forms=oldforms.get(ch,[]),korean_forms=forms,kokuji=False,words=wordlist))
source={name:hashlib.sha256((D/name).read_bytes()).hexdigest() for name in ['kanjidic2.xml.gz','JMdict_e.gz','wikt-new14.json','Unihan_Variants.txt']}
(OUT/'kanji-additions-14.draft.json').write_text(json.dumps(dict(schema_version='kanji-v1',version='0.3.11-dev',count=14,status='source_matched_native_review_pending',sources=source,items=items),ensure_ascii=False,indent=2)+'\n')
(OUT/'kanji-additions-14.enrichment.json').write_text(json.dumps(dict(schema='jgg-kanji-enrichment-v1',version='0.3.11-dev',total=14,sources=source,items=overlay),ensure_ascii=False,separators=(',',':'))+'\n')
print('14 cards,',sum(len(x['example_words']) for x in items),'word associations; all readings/hun sourced; total 639')
