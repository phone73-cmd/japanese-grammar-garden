"""Original practice examples and held-out assessment contexts, additive to v0.3.9.
No source dictionary data or legacy arrays are rewritten by this builder.
"""
import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def bank(s):
 out=[]
 for line in s.strip().splitlines():
  jp,kana,ko=line.split('|');x=dict(jp=jp,kana=kana,ko=ko)
  for key,a,b in [('kot','은','는'),('koo','을','를'),('kos','이','가'),('kokw','과','와')]:x[key]=ko+(a if '가'<=ko[-1]<='힣' and (ord(ko[-1])-44032)%28 else b)
  out.append(x)
 return out
jobs=bank('''学生|がくせい|학생
会社員|かいしゃいん|회사원
先生|せんせい|선생님
医者|いしゃ|의사
看護師|かんごし|간호사
店員|てんいん|점원
駅員|えきいん|역무원
料理人|りょうりにん|요리사
大学生|だいがくせい|대학생
旅行者|りょこうしゃ|여행자''')
things=bank('''本|ほん|책
かばん|かばん|가방
時計|とけい|시계
傘|かさ|우산
切符|きっぷ|표
地図|ちず|지도
財布|さいふ|지갑
写真|しゃしん|사진
鍵|かぎ|열쇠
帽子|ぼうし|모자''')
places=bank('''駅|えき|역
ホテル|ほてる|호텔
公園|こうえん|공원
図書館|としょかん|도서관
空港|くうこう|공항
学校|がっこう|학교
病院|びょういん|병원
銀行|ぎんこう|은행
入口|いりぐち|입구
出口|でぐち|출구''')
food=bank('''水|みず|물
お茶|おちゃ|차
コーヒー|こーひー|커피
ジュース|じゅーす|주스
パン|ぱん|빵
おにぎり|おにぎり|주먹밥
サラダ|さらだ|샐러드
カレー|かれー|카레
うどん|うどん|우동
ケーキ|けーき|케이크''')
# Explicit inflections; readings and Korean translations are authored, not inferred from kanji.
verbs=[]
raw='''本を読む|ほん を よむ|책을 읽다|本を読みます|ほん を よみます|책을 읽습니다|本を読んで|ほん を よんで|책을 읽고|本を読んだ|ほん を よんだ|책을 읽었다|本を読まない|ほん を よまない|책을 읽지 않는다
水を飲む|みず を のむ|물을 마시다|水を飲みます|みず を のみます|물을 마십니다|水を飲んで|みず を のんで|물을 마시고|水を飲んだ|みず を のんだ|물을 마셨다|水を飲まない|みず を のまない|물을 마시지 않는다
パンを食べる|ぱん を たべる|빵을 먹다|パンを食べます|ぱん を たべます|빵을 먹습니다|パンを食べて|ぱん を たべて|빵을 먹고|パンを食べた|ぱん を たべた|빵을 먹었다|パンを食べない|ぱん を たべない|빵을 먹지 않는다
駅へ行く|えき へ いく|역에 가다|駅へ行きます|えき へ いきます|역에 갑니다|駅へ行って|えき へ いって|역에 가고|駅へ行った|えき へ いった|역에 갔다|駅へ行かない|えき へ いかない|역에 가지 않는다
写真を見る|しゃしん を みる|사진을 보다|写真を見ます|しゃしん を みます|사진을 봅니다|写真を見て|しゃしん を みて|사진을 보고|写真を見た|しゃしん を みた|사진을 봤다|写真を見ない|しゃしん を みない|사진을 보지 않는다
日本語を話す|にほんご を はなす|일본어를 말하다|日本語を話します|にほんご を はなします|일본어를 말합니다|日本語を話して|にほんご を はなして|일본어를 말하고|日本語を話した|にほんご を はなした|일본어를 말했다|日本語を話さない|にほんご を はなさない|일본어를 말하지 않는다
手紙を書く|てがみ を かく|편지를 쓰다|手紙を書きます|てがみ を かきます|편지를 씁니다|手紙を書いて|てがみ を かいて|편지를 쓰고|手紙を書いた|てがみ を かいた|편지를 썼다|手紙を書かない|てがみ を かかない|편지를 쓰지 않는다
音楽を聞く|おんがく を きく|음악을 듣다|音楽を聞きます|おんがく を ききます|음악을 듣습니다|音楽を聞いて|おんがく を きいて|음악을 듣고|音楽を聞いた|おんがく を きいた|음악을 들었다|音楽を聞かない|おんがく を きかない|음악을 듣지 않는다
家へ帰る|いえ へ かえる|집으로 돌아가다|家へ帰ります|いえ へ かえります|집으로 돌아갑니다|家へ帰って|いえ へ かえって|집으로 돌아가고|家へ帰った|いえ へ かえった|집으로 돌아갔다|家へ帰らない|いえ へ かえらない|집으로 돌아가지 않는다
宿題をする|しゅくだい を する|숙제를 하다|宿題をします|しゅくだい を します|숙제를 합니다|宿題をして|しゅくだい を して|숙제를 하고|宿題をした|しゅくだい を した|숙제를 했다|宿題をしない|しゅくだい を しない|숙제를 하지 않는다'''
for line in raw.splitlines():
 a=line.split('|');x={}
 for i,key in enumerate(['dic','mas','te','ta','nai']):
  x[key],x[key+'r'],x[key+'k']=a[i*3:i*3+3]
 x['stem']=x['mas'][:-2];x['stemr']=x['masr'][:-2]
 # Explicit Korean infinitive stem for a construction gloss; all endings use whole quoted actions.
 verbs.append(x)
# Templates deliberately include questions, negation, past, contrast and short responses.
# Each four-template set × ten contexts gives 40 distinct sentences. Eight are taught,
# at least thirty others are held out for assessment; lexical substitutions are not the only change.
spec={}
def S(n,slots,lines):spec[n]=(slots,[l.split('|') for l in lines.strip().splitlines()])
S(6,things,'''私は{jp}を持っています。|わたし は {kana} を もっています。|저는 {koo} 가지고 있습니다.
{jp}はここにあります。|{kana} は ここ に あります。|{kot} 여기에 있습니다.
これは{jp}ですか。|これ は {kana} ですか。|이것은 {ko}입니까?
{jp}を見せてください。|{kana} を みせて ください。|{koo} 보여 주세요.''')
S(7,jobs,'''私は{jp}です。|わたし は {kana} です。|저는 {ko}입니다.
兄は{jp}ではありません。|あに は {kana} では ありません。|형은 {ko}이 아닙니다.
父は{jp}でした。|ちち は {kana} でした。|아버지는 {ko}이었습니다.
あの人は{jp}ですか。|あの ひと は {kana} ですか。|저 사람은 {ko}입니까?''')
S(8,jobs,'''私は{jp}ですが、妹は学生です。|わたし は {kana} ですが、いもうと は がくせい です。|저는 {ko}이지만 여동생은 학생입니다.
だれが{jp}ですか。|だれ が {kana} ですか。|누가 {ko}입니까?
田中さんが{jp}です。|たなかさん が {kana} です。|다나카 씨가 {ko}입니다.
{jp}はいますが、医者はいません。|{kana} は いますが、いしゃ は いません。|{kot} 있지만 의사는 없습니다.''')
S(9,things,'''これは{jp}です。|これ は {kana} です。|이것은 {ko}입니다.
それは私の{jp}ではありません。|それ は わたし の {kana} では ありません。|그것은 제 {ko}이 아닙니다.
あの{jp}を見てください。|あの {kana} を みて ください。|저 {koo} 봐 주세요.
どの{jp}がいいですか。|どの {kana} が いい ですか。|어느 {kos} 좋습니까?''')
S(11,things,'''これは母の{jp}です。|これ は はは の {kana} です。|이것은 어머니의 {ko}입니다.
その{jp}はだれのですか。|その {kana} は だれ の ですか。|그 {kot} 누구 것입니까?
私の{jp}はここにありません。|わたし の {kana} は ここ に ありません。|제 {kot} 여기에 없습니다.
あれは友だちの{jp}でした。|あれ は ともだち の {kana} でした。|저것은 친구의 {ko}이었습니다.''')
S(12,places,'''ここは{jp}です。|ここ は {kana} です。|여기는 {ko}입니다.
そこは{jp}ではありません。|そこ は {kana} では ありません。|거기는 {ko}이 아닙니다.
あそこが{jp}です。|あそこ が {kana} です。|저기가 {ko}입니다.
{jp}はどこですか。|{kana} は どこ ですか。|{kot} 어디입니까?''')
S(13,things,'''この{jp}はいくらですか。|この {kana} は いくら ですか。|이 {kot} 얼마입니까?
だれが{jp}を持っていますか。|だれ が {kana} を もって いますか。|누가 {koo} 가지고 있습니까?
{jp}はどこにありますか。|{kana} は どこ に ありますか。|{kot} 어디에 있습니까?
どの{jp}を買いますか。|どの {kana} を かいますか。|어느 {koo} 사겠습니까?''')
S(14,things,'''この{jp}は新しいです。|この {kana} は あたらしい です。|이 {kot} 새것입니다.
古い{jp}を使います。|ふるい {kana} を つかいます。|오래된 {koo} 사용합니다.
小さい{jp}があります。|ちいさい {kana} が あります。|작은 {kos} 있습니다.
あの{jp}は高いですか。|あの {kana} は たかい ですか。|저 {kot} 비쌉니까?''')
S(15,things,'''この{jp}は高くないです。|この {kana} は たかくない です。|이 {kot} 비싸지 않습니다.
あの{jp}は安かったです。|あの {kana} は やすかった です。|저 {kot} 쌌습니다.
その{jp}は新しくなかったです。|その {kana} は あたらしくなかった です。|그 {kot} 새것이 아니었습니다.
この{jp}は大きかったですか。|この {kana} は おおきかった ですか。|이 {kot} 컸습니까?''')
S(16,places,'''この{jp}は静かです。|この {kana} は しずか です。|이 {kot} 조용합니다.
あそこに有名な{jp}があります。|あそこ に ゆうめいな {kana} が あります。|저기에 유명한 {kos} 있습니다.
ここは便利な{jp}です。|ここ は べんりな {kana} です。|여기는 편리한 {ko}입니다.
その{jp}はきれいですか。|その {kana} は きれい ですか。|그 {kot} 깨끗합니까?''')
S(17,places,'''あの{jp}は静かでした。|あの {kana} は しずか でした。|저 {kot} 조용했습니다.
この{jp}は便利ではありません。|この {kana} は べんり では ありません。|이 {kot} 편리하지 않습니다.
昔、その{jp}は有名ではありませんでした。|むかし、その {kana} は ゆうめい では ありませんでした。|옛날에 그 {kot} 유명하지 않았습니다.
その{jp}はきれいでしたか。|その {kana} は きれい でしたか。|그 {kot} 깨끗했습니까?''')
S(18,places,'''{jp}に猫がいます。|{kana} に ねこ が います。|{ko}에 고양이가 있습니다.
{jp}の前に木があります。|{kana} の まえ に き が あります。|{ko} 앞에 나무가 있습니다.
田中さんは{jp}にいません。|たなかさん は {kana} に いません。|다나카 씨는 {ko}에 없습니다.
{jp}に自動販売機がありますか。|{kana} に じどうはんばいき が ありますか。|{ko}에 자동판매기가 있습니까?''')
S(24,places,'''{jp}で友だちに会います。|{kana} で ともだち に あいます。|{ko}에서 친구를 만납니다.
{jp}に地図があります。|{kana} に ちず が あります。|{ko}에 지도가 있습니다.
三時に{jp}へ行きます。|さんじ に {kana} へ いきます。|세 시에 {ko}에 갑니다.
バスで{jp}へ行きました。|ばす で {kana} へ いきました。|버스로 {ko}에 갔습니다.''')
S(25,places,'''友だちと{jp}へ行きます。|ともだち と {kana} へ いきます。|친구와 {ko}에 갑니다.
{jp}から歩いて帰りました。|{kana} から あるいて かえりました。|{ko}에서 걸어서 돌아왔습니다.
明日、{jp}に来ますか。|あした、{kana} に きますか。|내일 {ko}에 오십니까?
家から{jp}までバスで行きます。|いえ から {kana} まで ばす で いきます。|집에서 {ko}까지 버스로 갑니다.''')
# Verb-focused units explicitly reuse fully specified inflection sets, not text substitutions.
S(21,verbs,'''毎日、{dic}。|まいにち、{dicr}。|매일 {dick}.
明日は{mas}。|あした は {masr}。|내일은 {mask}.
昨日、{ta}。|きのう、{tar}。|어제 {tak}.
今日は{nai}。|きょう は {nair}。|오늘은 {naik}.''')
S(22,verbs,'''私は{mas}。|わたし は {masr}。|저는 {mask}.
明日も{mas}。|あした も {masr}。|내일도 {mask}.
毎朝、{mas}。|まいあさ、{masr}。|매일 아침 {mask}.
今から{mas}か。|いま から {masr}か。|지금부터 {mask}까?''')
S(23,verbs,'''今日は{mas}。|きょう は {masr}。|오늘은 {mask}.
昨日は{stem}ませんでした。|きのう は {stemr}ませんでした。|어제는 ‘{dick}’라는 행동을 하지 않았습니다.
明日は{stem}ません。|あした は {stemr}ません。|내일은 ‘{dick}’라는 행동을 하지 않습니다.
先週も{stem}ましたか。|せんしゅう も {stemr}ましたか。|지난주에도 ‘{dick}’라는 행동을 했습니까?''')
S(26,verbs,'''{te}、少し休みます。|{ter}、すこし やすみます。|{tek} 조금 쉽니다.
{te}ください。|{ter} ください。|‘{dick}’라는 행동을 해 주세요.
昨日、{ta}。|きのう、{tar}。|어제 {tak}.
{te}から、電話します。|{ter} から、でんわ します。|‘{dick}’라는 행동을 한 다음 전화합니다.''')
S(27,verbs,'''もう一度、{te}ください。|もう いちど、{ter} ください。|한 번 더 ‘{dick}’라는 행동을 해 주세요.
ゆっくり{te}ください。|ゆっくり {ter} ください。|천천히 ‘{dick}’라는 행동을 해 주세요.
ここで{te}ください。|ここ で {ter} ください。|여기서 ‘{dick}’라는 행동을 해 주세요.
先に{te}ください。|さき に {ter} ください。|먼저 ‘{dick}’라는 행동을 해 주세요.''')
S(28,verbs,'''今、{te}います。|いま、{ter} います。|지금 ‘{dick}’라는 행동을 하고 있습니다.
毎日、{te}います。|まいにち、{ter} います。|매일 ‘{dick}’라는 행동을 하고 있습니다.
まだ{te}いません。|まだ {ter} いません。|아직 ‘{dick}’라는 행동을 하지 않았습니다.
昨日の今ごろは{te}いました。|きのう の いまごろ は {ter} いました。|어제 이맘때에는 ‘{dick}’라는 행동을 하고 있었습니다.''')
S(29,verbs,'''今日は{nai}。|きょう は {nair}。|오늘은 {naik}.
明日も{nai}。|あした も {nair}。|내일도 {naik}.
ここでは{nai}でください。|ここ では {nair}で ください。|여기서는 ‘{dick}’라는 행동을 하지 말아 주세요.
私はあまり{nai}。|わたし は あまり {nair}。|저는 ‘{dick}’라는 행동을 별로 하지 않는다.''')
S(31,verbs,'''{stem}たいです。|{stemr}たい です。|‘{dick}’라는 행동을 하고 싶습니다.
今は{stem}たくないです。|いま は {stemr}たくない です。|지금은 ‘{dick}’라는 행동을 하고 싶지 않습니다.
昨日は{stem}たかったです。|きのう は {stemr}たかった です。|어제는 ‘{dick}’라는 행동을 하고 싶었습니다.
明日、{stem}たいですか。|あした、{stemr}たい ですか。|내일 ‘{dick}’라는 행동을 하고 싶습니까?''')
S(32,things,'''新しい{jp}がほしいです。|あたらしい {kana} が ほしい です。|새 {koo} 갖고 싶습니다.
今は{jp}がほしくないです。|いま は {kana} が ほしくない です。|지금은 {koo} 원하지 않습니다.
昨日は{jp}がほしかったです。|きのう は {kana} が ほしかった です。|어제는 {koo} 갖고 싶었습니다.
どんな{jp}がほしいですか。|どんな {kana} が ほしい ですか。|어떤 {koo} 갖고 싶습니까?''')
S(33,verbs,'''ここで{te}もいいですか。|ここ で {ter}も いい ですか。|여기서 ‘{dick}’라는 행동을 해도 됩니까?
はい、{te}もいいですよ。|はい、{ter}も いい ですよ。|네, ‘{dick}’라는 행동을 해도 괜찮아요.
明日、{te}もいいですか。|あした、{ter}も いい ですか。|내일 ‘{dick}’라는 행동을 해도 됩니까?
先に{te}もいいですか。|さき に {ter}も いい ですか。|먼저 ‘{dick}’라는 행동을 해도 됩니까?''')
S(34,verbs,'''ここで{te}はいけません。|ここ で {ter}は いけません。|여기서 ‘{dick}’라는 행동을 하면 안 됩니다.
今は{te}はいけません。|いま は {ter}は いけません。|지금은 ‘{dick}’라는 행동을 하면 안 됩니다.
一人で{te}はいけません。|ひとり で {ter}は いけません。|혼자 ‘{dick}’라는 행동을 하면 안 됩니다.
許可なく{te}はいけません。|きょか なく {ter}は いけません。|허가 없이 ‘{dick}’라는 행동을 하면 안 됩니다.''')
S(35,verbs,'''{dic}ことができます。|{dicr} こと が できます。|‘{dick}’라는 행동을 할 수 있습니다.
今は{dic}ことができません。|いま は {dicr} こと が できません。|지금은 ‘{dick}’라는 행동을 할 수 없습니다.
ここで{dic}ことができますか。|ここ で {dicr} こと が できますか。|여기서 ‘{dick}’라는 행동을 할 수 있습니까?
一人で{dic}ことができました。|ひとり で {dicr} こと が できました。|혼자 ‘{dick}’라는 행동을 할 수 있었습니다.''')
S(36,verbs,'''一緒に{stem}ましょう。|いっしょ に {stemr}ましょう。|함께 ‘{dick}’라는 행동을 합시다.
先に{stem}ましょう。|さき に {stemr}ましょう。|먼저 ‘{dick}’라는 행동을 합시다.
あとで{stem}ましょう。|あと で {stemr}ましょう。|나중에 ‘{dick}’라는 행동을 합시다.
ここで{stem}ましょう。|ここ で {stemr}ましょう。|여기서 ‘{dick}’라는 행동을 합시다.''')
S(37,verbs,'''一緒に{stem}ませんか。|いっしょ に {stemr}ませんか。|함께 ‘{dick}’라는 행동을 하지 않을래요?
明日、{stem}ませんか。|あした、{stemr}ませんか。|내일 ‘{dick}’라는 행동을 하지 않을래요?
ここで{stem}ませんか。|ここ で {stemr}ませんか。|여기서 ‘{dick}’라는 행동을 하지 않을래요?
あとで{stem}ませんか。|あと で {stemr}ませんか。|나중에 ‘{dick}’라는 행동을 하지 않을래요?''')
S(38,things,'''この{jp}はあれより安いです。|この {kana} は あれ より やすい です。|이 {kot} 저것보다 쌉니다.
その{jp}のほうが軽いです。|その {kana} の ほう が かるい です。|그 {kos} 더 가볍습니다.
どの{jp}がいちばん新しいですか。|どの {kana} が いちばん あたらしい ですか。|어느 {kos} 가장 새것입니까?
この{jp}とあの{jp}と、どちらが大きいですか。|この {kana} と あの {kana} と、どちら が おおきい ですか。|이 {kokw} 저 {ko} 중 어느 쪽이 큽니까?''')
S(39,verbs,'''先に{ta}ほうがいいです。|さき に {tar} ほう が いい です。|먼저 ‘{dick}’라는 행동을 하는 편이 좋습니다.
今日は{nai}ほうがいいです。|きょう は {nair} ほう が いい です。|오늘은 ‘{dick}’라는 행동을 하지 않는 편이 좋습니다.
ゆっくり{ta}ほうがいいです。|ゆっくり {tar} ほう が いい です。|천천히 ‘{dick}’라는 행동을 하는 편이 좋습니다.
今から{ta}ほうがいいですか。|いま から {tar} ほう が いい ですか。|지금부터 ‘{dick}’라는 행동을 하는 편이 좋습니까?''')
S(41,places,'''{jp}は近いので、歩きます。|{kana} は ちかい ので、あるきます。|{kot} 가까우므로 걸어갑니다.
{jp}は遠いから、バスで行きます。|{kana} は とおい から、ばす で いきます。|{kot} 머니까 버스로 갑니다.
{jp}は静かなので、本を読みます。|{kana} は しずか なので、ほん を よみます。|{kot} 조용하므로 책을 읽습니다.
今日は休みなので、{jp}に行きません。|きょう は やすみ なので、{kana} に いきません。|오늘은 쉬는 날이므로 {ko}에 가지 않습니다.''')
S(42,things,'''この{jp}は高いですが、買います。|この {kana} は たかい ですが、かいます。|이 {kot} 비싸지만 삽니다.
{jp}を買いたいけど、お金がありません。|{kana} を かいたい けど、おかね が ありません。|{koo} 사고 싶지만 돈이 없습니다.
{jp}を探しているんですが。|{kana} を さがして いるん ですが。|{koo} 찾고 있는데요.
この{jp}は古いけど、まだ使えます。|この {kana} は ふるい けど、まだ つかえます。|이 {kot} 오래됐지만 아직 사용할 수 있습니다.''')
S(43,places,'''{jp}へ行きます。それから、家に帰ります。|{kana} へ いきます。それから、いえ に かえります。|{ko}에 갑니다. 그다음 집으로 돌아갑니다.
{jp}は近いです。そして、便利です。|{kana} は ちかい です。そして、べんり です。|{kot} 가깝습니다. 그리고 편리합니다.
{jp}へ行きたいです。でも、時間がありません。|{kana} へ いきたい です。でも、じかん が ありません。|{ko}에 가고 싶습니다. 하지만 시간이 없습니다.
まず、{jp}へ行きます。それから、昼ご飯を食べます。|まず、{kana} へ いきます。それから、ひるごはん を たべます。|먼저 {ko}에 갑니다. 그다음 점심을 먹습니다.''')
S(44,verbs,'''{te}から、出かけます。|{ter} から、でかけます。|‘{dick}’라는 행동을 한 다음 외출합니다.
{te}から、休みましょう。|{ter} から、やすみましょう。|‘{dick}’라는 행동을 한 다음 쉽시다.
{te}から、何をしますか。|{ter} から、なに を しますか。|‘{dick}’라는 행동을 한 다음 무엇을 합니까?
{te}から、友だちに電話しました。|{ter} から、ともだち に でんわ しました。|‘{dick}’라는 행동을 한 다음 친구에게 전화했습니다.''')
S(45,verbs,'''{ta}ことがあります。|{tar} こと が あります。|‘{dick}’라는 행동을 해 본 적이 있습니다.
まだ{ta}ことがありません。|まだ {tar} こと が ありません。|아직 ‘{dick}’라는 행동을 해 본 적이 없습니다.
日本で{ta}ことがありますか。|にほん で {tar} こと が ありますか。|일본에서 ‘{dick}’라는 행동을 해 본 적이 있습니까?
一人で{ta}ことはありません。|ひとり で {tar} こと は ありません。|혼자 ‘{dick}’라는 행동을 해 본 적은 없습니다.''')
S(46,verbs,'''{ta}ら、電話してください。|{tar}ら、でんわ して ください。|‘{dick}’라는 행동을 하고 나면 전화해 주세요.
{ta}ら、少し休みます。|{tar}ら、すこし やすみます。|‘{dick}’라는 행동을 하고 나면 조금 쉽니다.
{ta}ら、教えてください。|{tar}ら、おしえて ください。|‘{dick}’라는 행동을 하고 나면 알려 주세요.
{ta}ら、次は何をしますか。|{tar}ら、つぎ は なに を しますか。|‘{dick}’라는 행동을 하고 나면 다음에는 무엇을 합니까?''')
S(47,verbs,'''田中さんは{dic}と思います。|たなかさん は {dicr} と おもいます。|다나카 씨는 ‘{dick}’라는 행동을 할 것이라고 생각합니다.
田中さんは{nai}と思います。|たなかさん は {nair} と おもいます。|다나카 씨는 ‘{dick}’라는 행동을 하지 않을 것이라고 생각합니다.
田中さんは{ta}と思います。|たなかさん は {tar} と おもいます。|다나카 씨는 ‘{dick}’라는 행동을 했다고 생각합니다.
明日は{dic}と思いますか。|あした は {dicr} と おもいますか。|내일은 ‘{dick}’라는 행동을 할 것이라고 생각합니까?''')
S(48,places,'''あの{jp}は静かだそうです。|あの {kana} は しずか だ そう です。|저 {kot} 조용하다고 합니다.
新しい{jp}ができるそうです。|あたらしい {kana} が できる そう です。|새 {kos} 생긴다고 합니다.
あの{jp}は便利そうです。|あの {kana} は べんり そう です。|저 {kot} 편리해 보입니다.
その{jp}は近いそうです。|その {kana} は ちかい そう です。|그 {kot} 가깝다고 합니다.''')
S(49,places,'''明日、{jp}に伺います。|あした、{kana} に うかがいます。|내일 {ko}에 찾아뵙겠습니다.
先生は{jp}にいらっしゃいます。|せんせい は {kana} に いらっしゃいます。|선생님은 {ko}에 계십니다.
こちらが{jp}でございます。|こちら が {kana} で ございます。|이쪽이 {ko}입니다.
{jp}までご案内します。|{kana} まで ごあんない します。|{ko}까지 안내하겠습니다.''')
# Travel context sets have different request/confirmation/negative/past functions.
S(51,places,'''{jp}へ行く予定です。|{kana} へ いく よてい です。|{ko}에 갈 예정입니다.
{jp}の近くに泊まります。|{kana} の ちかく に とまります。|{ko} 근처에 묵습니다.
昨日、{jp}に着きました。|きのう、{kana} に つきました。|어제 {ko}에 도착했습니다.
{jp}には行きません。|{kana} には いきません。|{ko}에는 가지 않습니다.''')
S(52,places,'''このバスは{jp}に行きますか。|この ばす は {kana} に いきますか。|이 버스는 {ko}에 갑니까?
{jp}で降りてください。|{kana} で おりて ください。|{ko}에서 내려 주세요.
{jp}までの切符をください。|{kana} まで の きっぷ を ください。|{ko}까지 가는 표를 주세요.
{jp}まで乗り換えは必要ですか。|{kana} まで のりかえ は ひつよう ですか。|{ko}까지 환승이 필요합니까?''')
S(53,places,'''{jp}まで歩いて何分ですか。|{kana} まで あるいて なんぷん ですか。|{ko}까지 걸어서 몇 분입니까?
{jp}は右側にあります。|{kana} は みぎがわ に あります。|{kot} 오른쪽에 있습니다.
{jp}はこの道の先ですか。|{kana} は この みち の さき ですか。|{kot} 이 길 앞쪽에 있습니까?
{jp}への道を教えてください。|{kana} へ の みち を おしえて ください。|{ko}에 가는 길을 알려 주세요.''')
S(54,things,'''{jp}を預けてもいいですか。|{kana} を あずけても いい ですか。|{koo} 맡겨도 됩니까?
{jp}を部屋に忘れました。|{kana} を へや に わすれました。|{koo} 방에 두고 왔습니다.
{jp}はどこにありますか。|{kana} は どこ に ありますか。|{kot} 어디에 있습니까?
{jp}を受け取りに来ました。|{kana} を うけとり に きました。|{koo} 받으러 왔습니다.''')
S(55,food,'''{jp}を一つください。|{kana} を ひとつ ください。|{koo} 하나 주세요.
{jp}はありますか。|{kana} は ありますか。|{kos} 있습니까?
{jp}は持ち帰りでお願いします。|{kana} は もちかえり で おねがいします。|{kot} 포장 부탁드립니다.
{jp}をもう一つお願いします。|{kana} を もう ひとつ おねがいします。|{koo} 하나 더 부탁드립니다.''')
S(56,food,'''{jp}を二つお願いします。|{kana} を ふたつ おねがいします。|{koo} 두 개 부탁드립니다.
{jp}はまだ来ていません。|{kana} は まだ きて いません。|{kot} 아직 나오지 않았습니다.
{jp}には卵が入っていますか。|{kana} には たまご が はいって いますか。|{ko}에는 달걀이 들어 있습니까?
{jp}の注文を取り消せますか。|{kana} の ちゅうもん を とりけせますか。|{ko} 주문을 취소할 수 있습니까?''')
S(57,things,'''この{jp}を見せてください。|この {kana} を みせて ください。|이 {koo} 보여 주세요.
別の{jp}はありますか。|べつ の {kana} は ありますか。|다른 {kos} 있습니까?
この{jp}はカードで買えますか。|この {kana} は かーど で かえますか。|이 {kot} 카드로 살 수 있습니까?
昨日、この{jp}を買いました。|きのう、この {kana} を かいました。|어제 이 {koo} 샀습니다.''')
S(58,places,'''{jp}は何時からですか。|{kana} は なんじ から ですか。|{kot} 몇 시부터입니까?
{jp}の中で写真を撮ってもいいですか。|{kana} の なか で しゃしん を とっても いい ですか。|{ko} 안에서 사진을 찍어도 됩니까?
{jp}は今日は休みですか。|{kana} は きょう は やすみ ですか。|{kot} 오늘 쉬는 날입니까?
{jp}の地図はありますか。|{kana} の ちず は ありますか。|{ko} 지도가 있습니까?''')
S(59,things,'''{jp}をなくしました。|{kana} を なくしました。|{koo} 잃어버렸습니다.
{jp}を見ませんでしたか。|{kana} を みませんでしたか。|{koo} 못 보셨습니까?
{jp}が見つかりません。|{kana} が みつかりません。|{koo} 찾을 수 없습니다.
{jp}はどこに届ければいいですか。|{kana} は どこ に とどければ いい ですか。|{kot} 어디에 가져다주면 됩니까?''')
# Correct natural Korean connective forms, including 듣다 and 쓰다 irregularities.
kforms=[('책을 읽','책을 읽어','책을 읽은','책을 읽을','책을 읽으면','책을 읽읍시다','책을 읽는다'),('물을 마시','물을 마셔','물을 마신','물을 마실','물을 마시면','물을 마십시다','물을 마신다'),('빵을 먹','빵을 먹어','빵을 먹은','빵을 먹을','빵을 먹으면','빵을 먹읍시다','빵을 먹는다'),('역에 가','역에 가','역에 간','역에 갈','역에 가면','역에 갑시다','역에 간다'),('사진을 보','사진을 봐','사진을 본','사진을 볼','사진을 보면','사진을 봅시다','사진을 본다'),('일본어를 말하','일본어를 말해','일본어를 말한','일본어를 말할','일본어를 말하면','일본어를 말합시다','일본어를 말한다'),('편지를 쓰','편지를 써','편지를 쓴','편지를 쓸','편지를 쓰면','편지를 씁시다','편지를 쓴다'),('음악을 듣','음악을 들어','음악을 들은','음악을 들을','음악을 들으면','음악을 들읍시다','음악을 듣는다'),('집으로 돌아가','집으로 돌아가','집으로 돌아간','집으로 돌아갈','집으로 돌아가면','집으로 돌아갑시다','집으로 돌아간다'),('숙제를 하','숙제를 해','숙제를 한','숙제를 할','숙제를 하면','숙제를 합시다','숙제를 한다')]
for v,forms in zip(verbs,kforms):
 v.update(zip(['kstem','kconj','kdone','kfuture','kcond','kproposal','kplain'],forms));v['kmasq']=v['mask'][:-1]+'까';v['kpastq']=v['tak'][:-1]+'습니까'
for slots,_ in spec.values():
 for v in slots:
  if 'ko' in v:v['kopast']=v['ko']+('이었습니다' if v['kos'].endswith('이') else '였습니다')
replacements={
 '‘{dick}’라는 행동을 하지 않았습니다':'{kstem}지 않았습니다','‘{dick}’라는 행동을 하지 않습니다':'{kstem}지 않습니다','‘{dick}’라는 행동을 했습니까':'{kpastq}',
 '‘{dick}’라는 행동을 해 주세요':'{kconj} 주세요','‘{dick}’라는 행동을 한 다음':'{kdone} 다음','‘{dick}’라는 행동을 하고 있습니다':'{kstem}고 있습니다','‘{dick}’라는 행동을 하지 않았습니다':'{kstem}지 않았습니다','‘{dick}’라는 행동을 하고 있었습니다':'{kstem}고 있었습니다','‘{dick}’라는 행동을 하지 말아 주세요':'{kstem}지 말아 주세요','‘{dick}’라는 행동을 별로 하지 않는다':'{kstem}는 일을 별로 하지 않는다',
 '‘{dick}’라는 행동을 하고 싶':'{kstem}고 싶','‘{dick}’라는 행동을 해도':'{kconj}도','‘{dick}’라는 행동을 하면':'{kcond}',
 '‘{dick}’라는 행동을 할 수':'{kfuture} 수','‘{dick}’라는 행동을 합시다':'{kproposal}','‘{dick}’라는 행동을 하지 않을래요':'{kstem}지 않을래요',
 '‘{dick}’라는 행동을 하는 편':'{kstem}는 편','‘{dick}’라는 행동을 하지 않는 편':'{kstem}지 않는 편','‘{dick}’라는 행동을 해 본 적':'{kconj} 본 적',
 '‘{dick}’라는 행동을 하고 나면':'{kstem}고 나면','‘{dick}’라는 행동을 할 것':'{kfuture} 것','‘{dick}’라는 행동을 하지 않을 것':'{kstem}지 않을 것','‘{dick}’라는 행동을 했다고':'{tak}고',
 '{ko}이 아닙니다':'{kos} 아닙니다','{ko}이었습니다':'{kopast}','{mask}까':'{kmasq}','{dick}.':'{kplain}.'}
for n,(slots,templates) in spec.items():
 for row in templates:
  for a,b in replacements.items():row[2]=row[2].replace(a,b)
# Exclude a contradictory contrast and use a different staff role for this set.
spec[8]=(bank('''学生|がくせい|학생
会社員|かいしゃいん|회사원
先生|せんせい|선생님
運転手|うんてんしゅ|운전기사
看護師|かんごし|간호사
店員|てんいん|점원
駅員|えきいん|역무원
料理人|りょうりにん|요리사
大学生|だいがくせい|대학생
旅行者|りょこうしゃ|여행자'''),spec[8][1])
spec[8][1][0]=['私は{jp}です。妹は学生です。','わたし は {kana} です。いもうと は がくせい です。','저는 {ko}입니다. 여동생은 학생입니다.']
# Separate date/time/person counters, with attested special readings.
numbers=bank('''一時|いちじ|한 시
二時|にじ|두 시
三時|さんじ|세 시
四時|よじ|네 시
五時|ごじ|다섯 시
六時|ろくじ|여섯 시
七時|しちじ|일곱 시
八時|はちじ|여덟 시
九時|くじ|아홉 시
十時|じゅうじ|열 시''')
S(19,numbers,'''今は{jp}です。|いま は {kana} です。|지금은 {ko}입니다.
{jp}半に会いましょう。|{kana} はん に あいましょう。|{ko} 반에 만납시다.
明日は{jp}に出発します。|あした は {kana} に しゅっぱつ します。|내일은 {ko}에 출발합니다.
昨日は{jp}まで勉強しました。|きのう は {kana} まで べんきょう しました。|어제는 {ko}까지 공부했습니다.''')
# Word readings are explicitly supplied; katakana examples retain hiragana readings.
words=bank('''さかな|さかな|물고기
やま|やま|산
かわ|かわ|강
そら|そら|하늘
いぬ|いぬ|개
とり|とり|새
はな|はな|꽃
くるま|くるま|자동차
かさ|かさ|우산
まど|まど|창문
ほし|ほし|별
つき|つき|달
がっこう|がっこう|학교
きっぷ|きっぷ|표
ざっし|ざっし|잡지
しんぶん|しんぶん|신문
でんわ|でんわ|전화
えんぴつ|えんぴつ|연필
りょこう|りょこう|여행
じしょ|じしょ|사전
びょういん|びょういん|병원
びよういん|びよういん|미용실
きゃく|きゃく|손님
きやく|きやく|규약
おじさん|おじさん|아저씨
おじいさん|おじいさん|할아버지
おばさん|おばさん|아주머니
おばあさん|おばあさん|할머니
きて|きて|와 줘
きって|きって|우표
ここ|ここ|여기
こうこう|こうこう|고등학교
ほん|ほん|책
にほん|にほん|일본
りんご|りんご|사과
みかん|みかん|귤
きゅうり|きゅうり|오이
きょう|きょう|오늘
きのう|きのう|어제
あした|あした|내일
にゅうがく|にゅうがく|입학
じゅぎょう|じゅぎょう|수업
しゅくだい|しゅくだい|숙제
おちゃ|おちゃ|차
まっすぐ|まっすぐ|똑바로
けっこん|けっこん|결혼
しょくどう|しょくどう|식당
ちょっと|ちょっと|조금''')
katwords=bank('''アイス|あいす|아이스크림
エアコン|えあこん|에어컨
カーテン|かーてん|커튼
コート|こーと|코트
コンビニ|こんびに|편의점
スーパー|すーぱー|슈퍼마켓
タオル|たおる|수건
ノート|のーと|공책
パソコン|ぱそこん|컴퓨터
ベッド|べっど|침대
ボール|ぼーる|공
ラジオ|らじお|라디오
レストラン|れすとらん|식당
トイレ|といれ|화장실
メニュー|めにゅー|메뉴
チケット|ちけっと|티켓
シャツ|しゃつ|셔츠
シャワー|しゃわー|샤워
ジュース|じゅーす|주스
チョコレート|ちょこれーと|초콜릿
ファイル|ふぁいる|파일
フィルム|ふぃるむ|필름
フェリー|ふぇりー|페리
ティッシュ|てぃっしゅ|티슈''')
# Transliteration from explicit kana, retaining word/particle boundaries during conversion.
base=json.loads((ROOT/'course-data.js').read_text().split('window.JGG_COURSE_DATA=',1)[1].strip().rstrip(';'))
roman={x['reading']:x['romaji'] for rows in base['kana'].values() for x in rows}
roman.update({'ぁ':'a','ぃ':'i','ぅ':'u','ぇ':'e','ぉ':'o','ゃ':'ya','ゅ':'yu','ょ':'yo','ゔ':'vu'})
def romaji(kana):
 def token(t):
  if t in ['は','へ','を','では','には']:return {'は':'wa','へ':'e','を':'o','では':'dewa','には':'niwa'}[t]
  out='';i=0;gem=False
  while i<len(t):
   c=t[i]
   if c=='っ':gem=True;i+=1;continue
   if c=='ー':out+=next((v for v in out[::-1] if v in 'aeiou'),'');i+=1;continue
   pair=t[i:i+2];r=roman.get(pair)
   if r:i+=2
   else:r=roman.get(c,{'。':'.','、':',','？':'?'}.get(c,c));i+=1
   if gem:out+=('t' if r.startswith('ch') else r[0]);gem=False
   if out.endswith('n') and r and r[0] in 'aiueoy':out+="'"
   out+=r
  return out
 return ' '.join(token(t) for t in kana.split())
def example(row):
 jp,kana,ko=row
 assert not re.search('[一-龯ァ-ヶ]',kana),row
 return [jp,kana.replace(' ',''),romaji(kana),ko]
html=(ROOT/'index.html').read_text();prefix=html[html.index('const makeQ='):html.index('\nlet state=')].replace('window.JGG_PRACTICE.extend(content);','')
code='global.window={};'+(ROOT/'grammar-lessons.js').read_text()+(ROOT/'course-data.js').read_text()+(ROOT/'course-runtime.js').read_text()+prefix+';console.log(JSON.stringify(content))'
original=json.loads(subprocess.run(['node'],input=code,text=True,capture_output=True,check=True).stdout)
for group,extra in [(places,'郵便局|ゆうびんきょく|우체국\n美術館|びじゅつかん|미술관'),(things,'眼鏡|めがね|안경\n携帯電話|けいたいでんわ|휴대전화'),(jobs,'建築家|けんちくか|건축가\n美容師|びようし|미용사'),(food,'サンドイッチ|さんどいっち|샌드위치\nスープ|すーぷ|수프')]:
 group.extend(bank(extra))
 for v in group:
  if 'ko' in v:v['kopast']=v['ko']+('이었습니다' if v['kos'].endswith('이') else '였습니다')
result={}
for n,(slots,templates) in spec.items():
 rows=[[a.format(**v) for a in t] for t in templates for v in slots]
 assert len({r[0] for r in rows})==len(rows),(n,'duplicate')
 old={e[0] for e in original[str(n)]['examples']};available=[i for i,r in enumerate(rows) if r[0] not in old];taught=[]
 for k in range(4):
  candidates=[i for i in available if i//len(slots)==k]
  shift=(k*2)%len(candidates);taught.extend((candidates[shift:]+candidates[:shift])[:2])
 result[str(n)]={'examples':[example(rows[i]) for i in taught], 'assessments':[example(rows[i]) for i in available if i not in taught]}
 assert len(result[str(n)]['assessments'])>=30,(n,len(result[str(n)]['assessments']))

for n,source in [(1,words[:12]),(2,words[12:]),(4,katwords[:12]),(5,katwords[12:])]:
 result[str(n)]={'examples':[example([x['jp'],x['kana'],x['ko']]) for x in source[:8]],'assessments':[]}
def mora(kana):return sum(c not in 'ゃゅょぁぃぅぇぉ' and ('ぁ'<=c<='ゖ' or c=='ー') for c in kana)
# First eight are explicitly contrasted, remaining forty are held-out mora contexts.
contrast=[words[i] for i in [20,21,22,23,24,25,30,31]]
exclude={e[0] for e in original['3']['examples']}|{x['jp'] for x in contrast}
result['3']={'examples':[example([x['jp'],x['kana'],x['ko']]) for x in contrast],'assessments':[example([x['jp'],x['kana'],x['ko']]) for x in words if x['jp'] not in exclude],'mora':True}
assert len(result)==54,sorted(result)
# Date and counter detail is taught explicitly in 19; retain the eight-example target.
result['19']['examples']=[example(x.split('|')) for x in '''一日は休みです。|ついたち は やすみ です。|1일은 쉬는 날입니다.
二日に出発します。|ふつか に しゅっぱつ します。|2일에 출발합니다.
二十日に帰ります。|はつか に かえります。|20일에 돌아갑니다.
一人で来ました。|ひとり で きました。|혼자 왔습니다.
子どもは二人です。|こども は ふたり です。|아이는 두 명입니다.
三つください。|みっつ ください。|세 개 주세요.
一分待ってください。|いっぷん まって ください。|1분 기다려 주세요.
六分かかります。|ろっぷん かかります。|6분 걸립니다.'''.splitlines()]
# 717 taught examples: existing 237 + eight per lesson, including review units.
for n in [10,20,30,40,50,60]:
 rows=[result[str(i)]['examples'][0] for i in range(n-9,n)]
 result[str(n)]={'examples':rows[:8],'assessments':[]}
out=dict(schema='jgg-practice-v1',version='0.3.10-dev',lessons=result,editorial_status='authored_draft_structure_checked_not_native_review')
(ROOT/'practice-data.js').write_text('/* Original authored practice; scripts/build_practice.py. */\nwindow.JGG_PRACTICE_DATA='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
print('Added examples',sum(len(x['examples']) for x in result.values()),'held-out contexts',sum(len(x['assessments']) for x in result.values()))
# Two new four-turn dialogues per travel lesson, appended to the original dialogue.
dialogues={
51:'''직원|滞在期間はどのくらいですか。|たいざい きかん は どのくらい ですか。|체류 기간은 얼마나 됩니까?
나|四日間です。|よっかかん です。|4일간입니다.
직원|どこに泊まりますか。|どこ に とまりますか。|어디에 묵습니까?
나|難波のホテルです。|なんば の ほてる です。|난바에 있는 호텔입니다.
직원|帰りの航空券はありますか。|かえり の こうくうけん は ありますか。|돌아가는 항공권이 있습니까?
나|はい、あります。|はい、あります。|네, 있습니다.
직원|見せてください。|みせて ください。|보여 주세요.
나|はい、こちらです。|はい、こちら です。|네, 여기 있습니다.''',
52:'''나|難波までいくらですか。|なんば まで いくら ですか。|난바까지 얼마입니까?
직원|二百円です。|にひゃくえん です。|200엔입니다.
나|この券売機で買えますか。|この けんばいき で かえますか。|이 발매기에서 살 수 있습니까?
직원|はい、買えます。|はい、かえます。|네, 살 수 있습니다.
나|どのホームですか。|どの ほーむ ですか。|어느 승강장입니까?
직원|二番ホームです。|にばん ほーむ です。|2번 승강장입니다.
나|乗り換えは必要ですか。|のりかえ は ひつよう ですか。|환승이 필요합니까?
직원|いいえ、必要ありません。|いいえ、ひつよう ありません。|아니요, 필요하지 않습니다.''',
53:'''나|ここからホテルまで遠いですか。|ここ から ほてる まで とおい ですか。|여기서 호텔까지 멉니까?
상대|歩いて十分ぐらいです。|あるいて じゅっぷん ぐらい です。|걸어서 10분 정도입니다.
나|この道をまっすぐですか。|この みち を まっすぐ ですか。|이 길로 곧장 가면 됩니까?
상대|はい、まっすぐです。|はい、まっすぐ です。|네, 곧장 가시면 됩니다.
나|この近くにエレベーターはありますか。|この ちかく に えれべーたー は ありますか。|이 근처에 엘리베이터가 있습니까?
상대|あの建物の中にあります。|あの たてもの の なか に あります。|저 건물 안에 있습니다.
나|入口は左ですか。|いりぐち は ひだり ですか。|입구는 왼쪽입니까?
상대|いいえ、右です。|いいえ、みぎ です。|아니요, 오른쪽입니다.''',
54:'''나|チェックアウトは何時までですか。|ちぇっくあうと は なんじ まで ですか。|체크아웃은 몇 시까지입니까?
직원|十一時までです。|じゅういちじ まで です。|11시까지입니다.
나|その後、荷物を預けてもいいですか。|その あと、にもつ を あずけても いい ですか。|그 후에 짐을 맡겨도 됩니까?
직원|はい、大丈夫です。|はい、だいじょうぶ です。|네, 괜찮습니다.
나|Wi-Fiのパスワードを教えてください。|わいふぁい の ぱすわーど を おしえて ください。|와이파이 비밀번호를 알려 주세요.
직원|こちらに書いてあります。|こちら に かいて あります。|여기에 적혀 있습니다.
나|ありがとうございます。朝食は何階ですか。|ありがとう ございます。ちょうしょく は なんかい ですか。|감사합니다. 아침 식사는 몇 층입니까?
직원|二階です。|にかい です。|2층입니다.''',
55:'''직원|サイズはいかがなさいますか。|さいず は いかが なさいますか。|크기는 어떻게 하시겠습니까?
나|小さいサイズでお願いします。|ちいさい さいず で おねがいします。|작은 크기로 부탁드립니다.
직원|ほかにご注文はありますか。|ほか に ごちゅうもん は ありますか。|그 밖에 주문하실 것이 있습니까?
나|いいえ、それだけです。|いいえ、それだけ です。|아니요, 그것뿐입니다.
나|アイスコーヒーをお願いします。|あいすこーひー を おねがいします。|아이스커피 부탁드립니다.
직원|店内でお召し上がりですか。|てんない で おめしあがり ですか。|매장에서 드시겠습니까?
나|はい、店内でお願いします。|はい、てんない で おねがいします。|네, 매장에서 마시겠습니다.
직원|かしこまりました。|かしこまりました。|알겠습니다.''',
56:'''나|これは辛いですか。|これ は からい ですか。|이것은 맵습니까?
직원|少し辛いです。|すこし からい です。|조금 맵습니다.
나|辛くない料理はありますか。|からくない りょうり は ありますか。|맵지 않은 요리가 있습니까?
직원|こちらはいかがですか。|こちら は いかが ですか。|이것은 어떠십니까?
나|お会計をお願いします。|おかいけい を おねがいします。|계산 부탁드립니다.
직원|お支払いはどうなさいますか。|おしはらい は どう なさいますか。|결제는 어떻게 하시겠습니까?
나|カードでお願いします。|かーど で おねがいします。|카드로 부탁드립니다.
직원|こちらにお願いします。|こちら に おねがいします。|이쪽에 부탁드립니다.''',
57:'''나|試着してもいいですか。|しちゃく しても いい ですか。|입어 봐도 됩니까?
직원|はい、試着室はあちらです。|はい、しちゃくしつ は あちら です。|네, 탈의실은 저쪽입니다.
나|もう少し大きいサイズはありますか。|もう すこし おおきい さいず は ありますか。|조금 더 큰 크기가 있습니까?
직원|確認いたします。|かくにん いたします。|확인하겠습니다.
나|これをください。|これ を ください。|이것을 주세요.
직원|袋は必要ですか。|ふくろ は ひつよう ですか。|봉투가 필요합니까?
나|いいえ、大丈夫です。|いいえ、だいじょうぶ です。|아니요, 괜찮습니다.
직원|ありがとうございます。|ありがとう ございます。|감사합니다.''',
58:'''나|待ち時間はどのくらいですか。|まちじかん は どのくらい ですか。|대기 시간은 얼마나 됩니까?
직원|三十分ぐらいです。|さんじゅっぷん ぐらい です。|30분 정도입니다.
나|ここに並べばいいですか。|ここ に ならべば いい ですか。|여기에 줄을 서면 됩니까?
직원|はい、こちらです。|はい、こちら です。|네, 이쪽입니다.
나|写真を撮ってもいいですか。|しゃしん を とっても いい ですか。|사진을 찍어도 됩니까?
직원|ここでは撮らないでください。|ここ では とらないで ください。|여기서는 찍지 말아 주세요.
나|わかりました。出口はどこですか。|わかりました。でぐち は どこ ですか。|알겠습니다. 출구는 어디입니까?
직원|右側です。|みぎがわ です。|오른쪽입니다.''',
59:'''나|すみません、助けてください。|すみません、たすけて ください。|죄송하지만 도와주세요.
상대|どうしましたか。|どう しましたか。|무슨 일이 있으십니까?
나|子どもが見つかりません。|こども が みつかりません。|아이를 찾을 수 없습니다.
상대|係員を呼びます。|かかりいん を よびます。|직원을 부르겠습니다.
상대|お名前を教えてください。|おなまえ を おしえて ください。|이름을 알려 주세요.
나|すみません、ゆっくりお願いします。|すみません、ゆっくり おねがいします。|죄송하지만 천천히 부탁드립니다.
상대|お名前は何ですか。|おなまえ は なん ですか。|이름이 무엇입니까?
나|タナカです。|たなか です。|다나카입니다.'''}
for n,s in dialogues.items():
 rows=[]
 for l in s.splitlines():
  role,jp,kana,ko=l.split('|');e=example([jp,kana,ko]);rows.append([role,*e])
 result[str(n)]['dialogues']=[rows[:4],rows[4:]]
# Re-emit after adding dialogue data.
(ROOT/'practice-data.js').write_text('/* Original authored practice; scripts/build_practice.py. */\nwindow.JGG_PRACTICE_DATA='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
original_romaji={
51:'nihon e wa nani o shi ni kimashita ka.|kankou de kimashita.|nanpaku shimasu ka.|sanpaku shimasu.',
52:'kono densha wa nanba ni ikimasu ka.|hai, ikimasu.|doko de orireba ii desu ka.|nanba eki de orite kudasai.',
53:'eki wa doko desu ka.|tsugi no kado o migi ni magatte kudasai.|migi desu ne.|hai. sono saki ni arimasu.',
54:'goyoyaku wa arimasu ka.|hai, yoyaku shite imasu.|onamae o onegai shimasu.|tanaka desu.',
55:'hotto koohii o hitotsu kudasai.|tennai de omeshiagari desu ka.|mochikaeri de onegai shimasu.|kashikomarimashita.',
56:'nanmei sama desu ka.|sannin desu.|gochuumon wa okimari desu ka.|kore o futatsu kudasai.',
57:'kore wa ikura desu ka.|nisen en desu.|kaado de haraemasu ka.|hai, tsukaemasu.',
58:'chiketto o misete kudasai.|hai, douzo.|iriguchi wa doko desu ka.|achira desu.',
59:'dou shimashita ka.|saifu o nakushimashita.|doko de nakushimashita ka.|eki da to omoimasu.'}
for n,r in original_romaji.items():result[str(n)]['originalDialogueRomaji']=r.split('|')
(ROOT/'practice-data.js').write_text('/* Original authored practice; scripts/build_practice.py. */\nwindow.JGG_PRACTICE_DATA='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
