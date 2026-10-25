"""Build an offline index from actual lessons and kanji, with JMdict POS evidence.
python scripts/build_library.py /path/to/dictionaries
"""
from pathlib import Path
import sys,json,gzip,subprocess,re,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];D=Path(sys.argv[1])
loadjs=lambda f,n:json.loads((ROOT/f).read_text().split(n+'=')[1].strip().rstrip(';'))
html=(ROOT/'index.html').read_text();prefix=html[html.index('const titles='):html.index('\nlet state=')]
code='global.window={};'+''.join((ROOT/f).read_text() for f in ['grammar-lessons.js','course-data.js','course-runtime.js','practice-data.js','practice-runtime.js'])+prefix+';console.log(JSON.stringify({content,titles}))'
raw=json.loads(subprocess.run(['node'],input=code,text=True,capture_output=True,check=True).stdout);content=raw['content'];titles=raw['titles'];c=loadjs('course-data.js','window.JGG_COURSE_DATA');p=loadjs('practice-data.js','window.JGG_PRACTICE_DATA')
base=ROOT/'data/kanji';original=[x for f in [*(sorted(base.glob('kanji-stage-*-100.draft.json'))),base/'kanji-extra-125.draft.json',base/'kanji-additions-14.draft.json'] for x in json.loads(f.read_text())['items']]
overlay={x['id']:x for f in [base/'kanji-enrichment.json',base/'kanji-additions-14.enrichment.json'] for x in json.loads(f.read_text())['items']}
assert len(original)==len(overlay)==639
entries=[];texts=[]
for key,d in content.items():
 n=int(key);add=c['lessons'].get(key,{});text=d['goal']+' '+d['explain']+' '+add.get('tip','')+' '+' '.join(' '.join(r) for r in add.get('table',[]));aliases={21:'辞書形 じしょけい',22:'ます形',26:'て形 テ形 てけい た形',29:'ない形',47:'普通形 ふつうけい',48:'そうです 様態 伝聞'}.get(n,'')
 entries.append(dict(id=f'lesson-{n}',kind='lesson',japanese=titles[n-1],reading='',meaning=d['goal'],keywords=[text,aliases],categories=['grammar'],lessonId=n))
 texts.append((n,text))
 for i,e in enumerate(d['examples']):
  entries.append(dict(id=f'example-{n}-{i}',kind='example',japanese=e[0],reading=e[1],meaning=e[3],keywords=[e[2]],categories=['kana'] if n<=5 else ['phrase'],lessonId=n,exampleIndex=i));texts.append((n,e[0]))
 dialogues=[]
 if add.get('dialogue'):dialogues.append([[r[0],r[1],r[2],'',r[3]] for r in add['dialogue']])
 dialogues+=p['lessons'][key].get('dialogues',[])
 for g,rows in enumerate(dialogues):
  for i,(role,ja,kana,romaji,ko) in enumerate(rows):
   entries.append(dict(id=f'dialogue-{n}-{g}-{i}',kind='dialogue',japanese=ja,reading=kana,meaning=ko,keywords=[role,romaji],categories=['phrase'],lessonId=n));texts.append((n,ja))
# Original vocabulary pairs and newly sourced words; each sense retains its Korean gloss.
words={}
for x in original:
 d=overlay[x['id']];keys=[*d['korean_readings'],*(v['gloss'] for v in d['korean_glosses']),*(v['reading'] for v in d['korean_glosses']),*(r.replace('.','').replace('-','') for r in d['on']+d['kun']),*(v['character'] for v in d['korean_forms'])]
 entries.append(dict(id='card-'+x['id'],kind='kanji',japanese=x['character'],reading=' · '.join(d['korean_readings']),meaning=' · '.join(g['gloss']+' '+g['reading'] for g in d['korean_glosses']),keywords=keys,categories=['kanji'],kanjiId=x['id']))
 for w in d['words']+x['example_words']:
  k=w['word'],w['reading'],w['meaning_ko'];word=words.setdefault(k,dict(word=w['word'],reading=w['reading'],meaning=w['meaning_ko'],kanjiIds=[]));
  if x['id'] not in word['kanjiIds']:word['kanjiIds'].append(x['id'])
requested={(w['word'],w['reading']) for w in words.values()};tags={pair:set() for pair in requested};seqs={pair:[] for pair in requested}
for _,e in ET.iterparse(gzip.open(D/'JMdict_e.gz'),events=['end']):
 if e.tag!='entry':continue
 forms={v.text for v in e.findall('k_ele/keb')};pairs=set()
 for r in e.findall('r_ele'):
  reading=r.findtext('reb');restrict={v.text for v in r.findall('re_restr')}
  pairs.update((form,reading) for form in (forms&restrict if restrict else forms) if (form,reading) in requested)
 if pairs:
  inherited=[]
  for sense in e.findall('sense'):
   own=[v.text for v in sense.findall('pos') if v.text]
   if own:inherited=own
   sk={v.text for v in sense.findall('stagk')};sr={v.text for v in sense.findall('stagr')}
   for pair in pairs:
    if (not sk or pair[0] in sk) and (not sr or pair[1] in sr):tags[pair].update(inherited)
  for pair in pairs:seqs[pair].append(e.findtext('ent_seq'))
 e.clear()
def classify(pos):
 out=set()
 for s in pos:
  s=s.lower()
  if re.search(r'\bnouns?\b',s) and 'adjectival' not in s:out.add('noun')
  if re.search(r'\bverb\b',s):out.add('verb')
  if 'keiyoushi' in s:out.add('i_adj')
  if 'keiyodoshi' in s:out.add('na_adj')
  if 'adverb' in s:out.add('adverb')
  if 'pronoun' in s:out.add('pronoun')
  if s=='particle':out.add('particle')
  if 'conjunction' in s:out.add('conjunction')
  if 'counter' in s:out.add('counter')
  if 'expressions' in s:out.add('phrase')
 return sorted(out) or ['unclassified']
for i,w in enumerate(words.values()):
 pair=w['word'],w['reading'];related=sorted({n for n,t in texts if w['word'] in t});entries.append(dict(id=f'word-{i}',kind='word',japanese=w['word'],reading=w['reading'],meaning=w['meaning'],keywords=[],categories=classify(tags[pair]),kanjiId=w['kanjiIds'][0],kanjiIds=list(dict.fromkeys(x['id'] for ch in w['word'] for x in original if x['character']==ch)),relatedLessons=related,pos_evidence=sorted(tags[pair]),dictionary_entry_sequences=seqs[pair]))
# Explicit pedagogical entries for function words and patterns; no suffix-based guesses.
functions={
'pronoun':[(x,x,k,9) for x,k in [('これ','이것'),('それ','그것'),('あれ','저것'),('この','이 + 명사'),('その','그 + 명사'),('あの','저 + 명사')]]+[(x,x,k,12) for x,k in [('ここ','여기'),('そこ','거기'),('あそこ','저기')]],
'interrogative':[(x,r,k,13) for x,r,k in [('だれ','だれ','누구'),('いつ','いつ','언제'),('どこ','どこ','어디'),('いくら','いくら','얼마'),('何','なに・なん','무엇'),('どう','どう','어떻게'),('どれ','どれ','어느 것'),('どの','どの','어느 + 명사')]],
'particle':[(x,x,k,n) for x,k,n in [('は','화제·대비',8),('が','주어·새 정보',8),('を','목적어',24),('に','시각·도착점·존재 장소',24),('で','행동 장소·수단',24),('へ','이동 방향',25),('と','동행·나열',25),('の','소유·소속·종류',11),('から','출발점',25),('まで','도착 범위',25),('より','비교 기준',38)]],
'conjunction':[(x,x,k,43) for x,k in [('そして','그리고'),('それから','그다음에'),('でも','하지만')]],
'adverb':[(x,x,k,n) for x,k,n in [('ゆっくり','천천히',59),('まっすぐ','똑바로',53),('まだ','아직',28),('あまり','별로',29)]],
'counter':[(x,r,k,19) for x,r,k in [('一人','ひとり','한 명'),('二人','ふたり','두 명'),('一つ','ひとつ','한 개'),('二つ','ふたつ','두 개'),('三つ','みっつ','세 개'),('四時','よじ','네 시'),('一日','ついたち・いちにち','1일·하루')]],
'grammar':[(x,r,k,n) for x,r,k,n in [('です','です','명사 정중 표현',7),('ます','ます','동사 정중 표현',22),('てください','てください','행동 부탁',27),('てもいい','てもいい','허락',33),('てはいけません','てはいけません','금지',34),('たい','たい','행동 희망',31),('ほしい','ほしい','물건 희망',32),('と思います','とおもいます','생각·의견',47),('たことがある','たことがある','경험',45),('ています','ています','진행·상태',28),('たら','たら','조건',46),('そうです','そうです','모양·전달',48)]],
'greeting':[(x,x,k,n) for x,k,n in [('ありがとうございます','감사합니다',54),('すみません','죄송합니다·실례합니다',59),('お願いします','부탁드립니다',54),('はい、どうぞ','네, 여기 있습니다',58)]]}
for cat,rows in functions.items():
 for i,(ja,reading,ko,n) in enumerate(rows):
  if cat=='particle':reading={'は':'わ','へ':'え','を':'お'}.get(ja,reading)
  entries.append(dict(id=f'function-{cat}-{i}',kind='expression',japanese=ja,reading=reading,meaning=ko,keywords=[],categories=[cat],lessonId=n,classification_source='explicit-editorial-study-category'))
assert len({e['id'] for e in entries})==len(entries)
result=dict(license='Derived EDRDG and Wiktionary dictionary data: CC BY-SA 4.0; original app text: see sources.html',schema='jgg-library-v1',version='0.3.11-dev',kanji_count=639,entries=entries,sources={'JMdict_url':'https://www.edrdg.org/pub/Nihongo/JMdict_e.gz','JMdict_sha256':hashlib.sha256((D/'JMdict_e.gz').read_bytes()).hexdigest(),'category_policy':'Restricted Japanese form/reading sense POS; explicit pedagogical tags for function words; unclassified kept visible'})
(ROOT/'data/library-index.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
print('Index entries',len(entries),'words',len(words),'POS unclassified',sum(e['categories']==['unclassified'] for e in entries))
