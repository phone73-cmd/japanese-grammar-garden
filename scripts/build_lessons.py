"""Build authored grammar drafts. Original 1/6/7 question indices stay untouched."""
from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text();source=html[html.index('const makeQ='):html.index('\nlet state=')].split('\nObject.assign(content,')[0]
legacy=json.loads(subprocess.run(['node','-e',source+';console.log(JSON.stringify(content))'],check=True,capture_output=True,text=True).stdout)
base={}
rows='あ:a い:i う:u え:e お:o か:ka き:ki く:ku け:ke こ:ko さ:sa し:shi す:su せ:se そ:so た:ta ち:chi つ:tsu て:te と:to な:na に:ni ぬ:nu ね:ne の:no は:ha ひ:hi ふ:fu へ:he ほ:ho ま:ma み:mi む:mu め:me も:mo や:ya ゆ:yu よ:yo ら:ra り:ri る:ru れ:re ろ:ro わ:wa を:o ん:n が:ga ぎ:gi ぐ:gu げ:ge ご:go ざ:za じ:ji ず:zu ぜ:ze ぞ:zo だ:da ぢ:ji づ:zu で:de ど:do ば:ba び:bi ぶ:bu べ:be ぼ:bo ぱ:pa ぴ:pi ぷ:pu ぺ:pe ぽ:po ぁ:a ぃ:i ぅ:u ぇ:e ぉ:o ゃ:ya ゅ:yu ょ:yo ゔ:vu'
base.update(x.split(':') for x in rows.split())
for stem,consonant in [('き','ky'),('ぎ','gy'),('し','sh'),('じ','j'),('ち','ch'),('に','ny'),('ひ','hy'),('び','by'),('ぴ','py'),('み','my'),('り','ry')]:
 for small,vowel in [('ゃ','a'),('ゅ','u'),('ょ','o')]:base[stem+small]=consonant+vowel
base.update({'てぃ':'ti','でぃ':'di','ふぁ':'fa','ふぃ':'fi','ふぇ':'fe','ふぉ':'fo','うぃ':'wi','うぇ':'we','うぉ':'wo','ちぇ':'che','しぇ':'she','じぇ':'je'})
def romaji(text):
 def token(t):
  if t in ['は','へ','を','では','には','とは']:return {'は':'wa','へ':'e','を':'o','では':'dewa','には':'niwa','とは':'towa'}[t]
  out='';i=0;double=False
  while i<len(t):
   c=t[i]
   if c=='っ':double=True;i+=1;continue
   if c=='ー':out+=next((v for v in out[::-1] if v in 'aeiou'),'');i+=1;continue
   pair=t[i:i+2];r=base.get(pair)
   if r:i+=2
   else:r=base.get(c,{'。':'.','、':',','？':'?'}.get(c,c));i+=1
   if double and r:out+=r[0];double=False
   out+=r
  return out
 return ' '.join(token(t) for t in text.split())
lessons={};current=None
for line in (root/'data/grammar/lesson-drafts.txt').read_text().splitlines():
 if not line:continue
 if line.startswith('@'):
  n,goal,explain=line[1:].split('|');current={'goal':goal,'explain':explain,'examples':[],'questions':[],'editorial_status':'authored_draft'};lessons[n]=current
 elif line.startswith('?'):
  prompt,correct,*rest=line[1:].split('|');*wrong,reason=rest;assert len(wrong)==3;current['questions'].append({'question':prompt,'choices':[correct,*wrong],'correct':0,'reason':reason})
 else:
  ja,kana,ko=line.split('|');current['examples'].append([ja,kana.replace(' ',''),romaji(kana),ko])
for n,d in lessons.items():
 assert len(d['examples'])==4,(n,'examples')
 assert len(d['questions'])==2,(n,'rules')
 questions=[]
 for i,e in enumerate(d['examples']):
  questions.append({'question':f'「{e[0]}」의 뜻은?','choices':[x[3] for x in d['examples']],'correct':i,'reason':f'{e[0]} → {e[3]} '+d['explain']})
  questions.append({'question':f'‘{e[3]}’에 맞는 일본어는?','choices':[x[0] for x in d['examples']],'correct':i,'reason':f'{e[3]} → {e[0]} '+d['explain']})
 d['questions']=questions+d['questions']
# Stage reviews use different source questions, not newly invented copies of old indices.
merged={**legacy,**lessons}
for n in [10,20,30,40,50,60]:
 ids=[str(i) for i in range(n-9,n) if str(i) in merged]
 questions=[]
 for offset in [0,1]:
  for key in ids:
   source=merged[key]['questions'];j=(len(questions)+offset*3)%len(source)
   q=dict(source[j]);q['question']=f'{key}과 복습 · '+q['question'];questions.append(q)
   if len(questions)==10:break
  if len(questions)==10:break
 examples=[merged[key]['examples'][0] for key in ids[-4:]]
 lessons[str(n)]={'goal':f'{(n-1)//10+1}단계에서 배운 표현을 함께 복습해요.','explain':'앞 단원들의 핵심 표현을 섞어서 연습합니다. 틀린 문제는 해설을 확인하고 해당 단원에서 다시 익혀 보세요.','examples':examples,'questions':questions,'editorial_status':'authored_draft'}
assert len(lessons)==57
for n,d in lessons.items():
 assert len(d['questions'])==10
 for q in d['questions']:
  assert len(q['choices'])==4 and len(set(q['choices']))==4,(n,q)
  assert 0<=q['correct']<4 and q['reason']
(root/'grammar-lessons.js').write_text('/* Japanese Grammar Garden: 57 independently authored lesson drafts. See docs/CONTENT-SOURCES.md. */\nwindow.JGG_LESSONS='+json.dumps(lessons,ensure_ascii=False,separators=(',',':'))+';\n')
(root/'data/grammar/CONTENT-STATUS.json').write_text(json.dumps({'version':'0.3.0-dev','legacy_lessons_preserved':[1,6,7],'new_lessons':57,'total_lessons':60,'new_questions':570,'total_questions':600,'example_fields':['Japanese','hiragana','romaji','Korean'],'status':'authored_draft_structure_checked_not_independent_native_review','sources_document':'docs/CONTENT-SOURCES.md'},ensure_ascii=False,indent=2)+'\n')
print('57 additional lessons, 570 new questions; original 30 questions unchanged.')
