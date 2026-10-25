"""Reproducible editorial overlay; raw authored arrays and stable indices stay intact."""
from pathlib import Path
import json,subprocess,re
R=Path(__file__).resolve().parents[1]
load=lambda p,n:json.loads((R/p).read_text().split(n+'=',1)[1].strip().rstrip(';'))
raw=load('practice-data.js','window.JGG_PRACTICE_DATA');c=load('course-data.js','window.JGG_COURSE_DATA')
roman={x['reading']:x['romaji'] for rows in c['kana'].values() for x in rows};roman.update({'ぁ':'a','ぃ':'i','ぅ':'u','ぇ':'e','ぉ':'o','ゃ':'ya','ゅ':'yu','ょ':'yo','ゔ':'vu'})
def romaji(kana):
 def token(t):
  if t in ['は','へ','を','では','には']:return {'は':'wa','へ':'e','を':'o','では':'dewa','には':'niwa'}[t]
  out='';i=0;gem=False
  while i<len(t):
   ch=t[i]
   if ch=='っ':gem=True;i+=1;continue
   if ch=='ー':out+=next((v for v in out[::-1] if v in 'aeiou'),'');i+=1;continue
   pair=t[i:i+2];v=roman.get(pair)
   if v:i+=2
   else:v=roman.get(ch,{'。':'.','、':','}.get(ch,ch));i+=1
   if gem:out+=('t' if v.startswith('ch') else v[0]);gem=False
   if out.endswith('n') and v and v[0] in 'aiueoy':out+="'"
   out+=v
  return out
 return ' '.join(token(t) for t in kana.split())
def row(jp,kana,ko):return [jp,kana.replace(' ',''),romaji(kana),ko]
patches=[]
def put(old,new,group):
 if old==new:return
 assert len(new)==4 and all(new),(old,new)
 patches.append({'group':group,'before':old,'after':new})
# G02: all ten verb contexts, four experience directions. Give the experience a salient setting.
experience=[
('本を読んだ','日本語の本を読んだ','にほんご の ほん を よんだ','일본어 책을 읽어'),
('水を飲んだ','山の水を飲んだ','やま の みず を のんだ','산에서 나는 물을 마셔'),
('パンを食べた','日本のパンを食べた','にほん の ぱん を たべた','일본 빵을 먹어'),
('駅へ行った','大阪の駅へ行った','おおさか の えき へ いった','오사카의 역에 가'),
('写真を見た','昔の大阪の写真を見た','むかし の おおさか の しゃしん を みた','옛 오사카 사진을 봐'),
('日本語を話した','店で日本語を話した','みせ で にほんご を はなした','가게에서 일본어로 말해'),
('手紙を書いた','日本語で手紙を書いた','にほんご で てがみ を かいた','일본어로 편지를 써'),
('音楽を聞いた','日本の音楽を聞いた','にほん の おんがく を きいた','일본 음악을 들어'),
('家へ帰った','夜中に歩いて家へ帰った','よなか に あるいて いえ へ かえった','한밤중에 걸어서 집에 돌아가'),
('宿題をした','日本の学校で宿題をした','にほん の がっこう で しゅくだい を した','일본 학교에서 숙제를 해')]
for e in raw['lessons']['45']['examples']+raw['lessons']['45']['assessments']:
 v=next(x for x in experience if x[0] in e[0]);_,jp,kana,ko=v
 if e[0].startswith('まだ'):new=row('まだ'+jp+'ことがありません。','まだ '+kana+' こと が ありません。','아직 '+ko+' 본 적이 없습니다.')
 elif e[0].startswith('日本で'):new=row(jp+'ことがありますか。',kana+' こと が ありますか。',ko+' 본 적이 있습니까?')
 elif e[0].startswith('一人で'):new=row('一人で'+jp+'ことはありません。','ひとり で '+kana+' こと は ありません。','혼자 '+ko+' 본 적은 없습니다.')
 else:new=row(jp+'ことがあります。',kana+' こと が あります。',ko+' 본 적이 있습니다.')
 put(e,new,'G02')
# G03: only progression rows with motion verbs; habitual/negative rows remain valid.
for e in raw['lessons']['28']['assessments']:
 if not e[0].startswith(('今、','昨日の今ごろは')):continue
 if '駅へ行って' not in e[0] and '家へ帰って' not in e[0]:continue
 station='駅へ行って' in e[0];dest,reading,ko=('駅','えき','역') if station else ('家','いえ','집')
 past=e[0].startswith('昨日');put(e,row(('昨日の今ごろは' if past else '今、')+dest+'に向かって'+('いました。' if past else 'います。'),('きのう の いまごろ は ' if past else 'いま、')+reading+' に むかって '+('いました。' if past else 'います。'),('어제 이맘때에는 ' if past else '지금 ')+ko+'으로'+' 향하고 '+('있었습니다.' if past else '있습니다.')),'G03')
# G04: name the service being asked about; keep the 12 place slots and their indices.
opening=[('駅','この駅の窓口は何時からですか。','この えき の まどぐち は なんじ から ですか。','이 역의 창구는 몇 시부터입니까?'),('ホテル','ホテルのチェックインは何時からですか。','ほてる の ちぇっくいん は なんじ から ですか。','호텔 체크인은 몇 시부터입니까?'),('公園','公園には何時から入れますか。','こうえん には なんじ から はいれますか。','공원에는 몇 시부터 들어갈 수 있습니까?'),('図書館','図書館は何時に開きますか。','としょかん は なんじ に あきますか。','도서관은 몇 시에 문을 엽니까?'),('空港','空港の店は何時からですか。','くうこう の みせ は なんじ から ですか。','공항의 가게는 몇 시부터입니까?'),('学校','学校の受付は何時からですか。','がっこう の うけつけ は なんじ から ですか。','학교의 접수는 몇 시부터입니까?'),('病院','病院の受付は何時からですか。','びょういん の うけつけ は なんじ から ですか。','병원의 접수는 몇 시부터입니까?'),('銀行','銀行の窓口は何時からですか。','ぎんこう の まどぐち は なんじ から ですか。','은행 창구는 몇 시부터입니까?'),('入口','入口は何時に開きますか。','いりぐち は なんじ に あきますか。','입구는 몇 시에 열립니까?'),('出口','出口は何時まで使えますか。','でぐち は なんじ まで つかえますか。','출구는 몇 시까지 이용할 수 있습니까?'),('郵便局','郵便局の窓口は何時からですか。','ゆうびんきょく の まどぐち は なんじ から ですか。','우체국 창구는 몇 시부터입니까?'),('美術館','美術館は何時に開きますか。','びじゅつかん は なんじ に あきますか。','미술관은 몇 시에 문을 엽니까?')]
for e in raw['lessons']['58']['examples']+raw['lessons']['58']['assessments']:
 for place,jp,kana,ko in opening:
  if e[0]==place+'は何時からですか。':put(e,row(jp,kana,ko),'G04')
 replacements={'駅':('駅の窓口','えき の まどぐち','역 창구'),'ホテル':('ホテルのレストラン','ほてる の れすとらん','호텔 식당'),'空港':('空港の店','くうこう の みせ','공항의 가게')}
 for place,(jp,kana,ko) in replacements.items():
  if e[0]==place+'は今日は休みですか。':put(e,row(jp+'は今日は休みですか。',kana+' は きょう は やすみ ですか。',ko+'는 오늘 쉬는 날입니까?'),'G04')
 for place,kana,ko in [('入口','いりぐち','입구'),('出口','でぐち','출구')]:
  if e[0]==place+'は今日は休みですか。':put(e,row('この'+place+'は今日は使えますか。','この '+kana+' は きょう は つかえますか。','이 '+ko+'는 오늘 이용할 수 있습니까?'),'G04')
# G05: replace the entire arbitrary 'alone' template with clear school/family situations.
prohibitions=[('本を読んで','歩きながら本を読んではいけません。','あるき ながら ほん を よんでは いけません。','걸으면서 책을 읽으면 안 됩니다.'),('水を飲んで','この図書館では水を飲んではいけません。','この としょかん では みず を のんでは いけません。','이 도서관에서는 물을 마시면 안 됩니다.'),('パンを食べて','この図書館ではパンを食べてはいけません。','この としょかん では ぱん を たべては いけません。','이 도서관에서는 빵을 먹으면 안 됩니다.'),('駅へ行って','夜中に子どもだけで駅へ行ってはいけません。','よなか に こども だけ で えき へ いっては いけません。','한밤중에 아이들끼리 역에 가면 안 됩니다.'),('写真を見て','試験中に写真を見てはいけません。','しけんちゅう に しゃしん を みては いけません。','시험 중에 사진을 보면 안 됩니다.'),('日本語を話して','試験中に友だちと話してはいけません。','しけんちゅう に ともだち と はなしては いけません。','시험 중에 친구와 이야기하면 안 됩니다.'),('手紙を書いて','試験中に手紙を書いてはいけません。','しけんちゅう に てがみ を かいては いけません。','시험 중에 편지를 쓰면 안 됩니다.'),('音楽を聞いて','授業中に音楽を聞いてはいけません。','じゅぎょうちゅう に おんがく を きいては いけません。','수업 중에 음악을 들으면 안 됩니다.'),('家へ帰って','授業中に家へ帰ってはいけません。','じゅぎょうちゅう に いえ へ かえっては いけません。','수업 중에 집에 돌아가면 안 됩니다.'),('宿題をして','試験中にほかの勉強をしてはいけません。','しけんちゅう に ほか の べんきょう を しては いけません。','시험 중에 다른 공부를 하면 안 됩니다.')]
for e in raw['lessons']['34']['examples']+raw['lessons']['34']['assessments']:
 if e[0].startswith('一人で'):
  _,jp,kana,ko=next(x for x in prohibitions if x[0] in e[0]);put(e,row(jp,kana,ko),'G05')
# G06/G07: identify the person visited and the finder rather than just a place/item.
for e in raw['lessons']['49']['examples']+raw['lessons']['49']['assessments']:
 if e[0].startswith('明日、') and e[0].endswith('に伺います。'):
  place=e[0].split('、',1)[1].removesuffix('に伺います。');kana=e[1].split('、',1)[1].removesuffix('にうかがいます。')
  ko=e[3].removeprefix('내일 ').removesuffix('에 찾아뵙겠습니다.')
  put(e,row('明日、'+place+'の係の方に会いに伺います。','あした、'+kana+' の かかり の かた に あい に うかがいます。','내일 '+ko+' 담당자분을 뵈러 가겠습니다.'),'G06')
for e in raw['lessons']['59']['examples']+raw['lessons']['59']['assessments']:
 if 'はどこに届ければいいですか。' in e[0]:put(e,row('落とし物を見つけました。この'+e[0],'おとしもの を みつけました。この '+e[1].split('はどこに',1)[0]+' は どこ に とどければ いい ですか。', '분실물을 발견했습니다. 이 '+e[3].replace('가져다주면','맡기면')),'G07')
# G08: plain Japanese stays plain in Korean; remove the indirect action gloss.
ko29=['나는 책을 별로 읽지 않는다.','나는 물을 별로 마시지 않는다.','나는 빵을 별로 먹지 않는다.','나는 역에 자주 가지 않는다.','나는 사진을 별로 보지 않는다.','나는 일본어로 자주 말하지 않는다.','나는 편지를 별로 쓰지 않는다.','나는 음악을 별로 듣지 않는다.','나는 집에 자주 돌아가지 않는다.','나는 숙제를 자주 하지 않는다.']
rows=[e for e in raw['lessons']['29']['examples']+raw['lessons']['29']['assessments'] if e[0].startswith('私はあまり')]
verbs=['本を読まない','水を飲まない','パンを食べない','駅へ行かない','写真を見ない','日本語を話さない','手紙を書かない','音楽を聞かない','家へ帰らない','宿題をしない']
for e in rows:
 i=next(i for i,v in enumerate(verbs) if v in e[0]);put(e,[e[0],e[1],e[2],ko29[i]],'G08')
assert len({p['before'][0] for p in patches})==len(patches)
out={'version':'0.3.13-dev','base_version':'0.3.12-dev','patches':patches,'sources':['https://www.irodori.jpf.go.jp/assets/data/starter/pdf/X_L18.pdf','https://www.jpf.go.jp/j/urawa/j_rsorcs/textbook/dl/setsumei/setsumei_all.pdf','https://www.bunka.go.jp/seisaku/kokugo_nihongo/kokugo_shisaku/keigo/chapter2/detail.html'],'status':'source_informed_editorial_revision_not_native_certification'}
(R/'editorial-data.js').write_text('/* Editorial corrections; scripts/build_editorial.py. */\nwindow.JGG_EDITORIAL_DATA='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
print('Editorial row mappings',len(patches))
