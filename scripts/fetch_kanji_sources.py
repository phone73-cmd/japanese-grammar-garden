from pathlib import Path
import sys,json,gzip,xml.etree.ElementTree as ET,urllib.request,urllib.parse,concurrent.futures,hashlib
app=Path(__file__).resolve().parents[1];out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
for name,url in [('kanjidic2.xml.gz','https://www.edrdg.org/kanjidic/kanjidic2.xml.gz'),('JMdict_e.gz','https://www.edrdg.org/pub/Nihongo/JMdict_e.gz'),('Unihan.zip','https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip')]:
 if not (out/name).exists():(out/name).write_bytes(urllib.request.urlopen(url,timeout=60).read())
import zipfile
with zipfile.ZipFile(out/'Unihan.zip') as z:(out/'Unihan_Variants.txt').write_bytes(z.read('Unihan_Variants.txt'))
chars=[x['character'] for f in sorted((app/'data/kanji').glob('kanji-stage-*.json')) for x in json.loads(f.read_text())['items']]+[x['character'] for x in json.loads((app/'data/kanji/kanji-extra-125.draft.json').read_text())['items']]
tree=ET.parse(gzip.open(out/'kanjidic2.xml.gz'));entries={e.findtext('literal'):e for e in tree.findall('character')}
codes={(cp.attrib['cp_type'],cp.text):e.findtext('literal') for e in entries.values() for cp in e.findall('codepoint/cp_value')}
variants={c:list(dict.fromkeys(codes.get((v.attrib['var_type'],v.text)) for v in entries[c].findall('misc/variant') if codes.get((v.attrib['var_type'],v.text)))) for c in chars}
(out/'variants.json').write_text(json.dumps(variants,ensure_ascii=False,indent=2))
titles=list(dict.fromkeys(chars+[v for vs in variants.values() for v in vs]));batches=[titles[i:i+40] for i in range(0,len(titles),40)]
def fetch(kv):
 i,batch=kv;path=out/f'wikt-batch-{i:02}.json'
 if path.exists():return i,len(json.loads(path.read_text()).get('query',{}).get('pages',{}))
 q={'action':'query','prop':'revisions','rvprop':'ids|timestamp|content','rvslots':'main','titles':'|'.join(batch),'format':'json'}
 url='https://ko.wiktionary.org/w/api.php?'+urllib.parse.urlencode(q)
 req=urllib.request.Request(url,headers={'User-Agent':'JapaneseGrammarGarden/0.3.8 (kanji audit; https://github.com/phone73-cmd/japanese-grammar-garden)'})
 try:
  data=urllib.request.urlopen(req,timeout=40).read();d=json.loads(data)
  if 'error' in d:raise ValueError(d['error'])
  path.write_bytes(data);return i,len(d['query']['pages'])
 except Exception as e:return i,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for result in ex.map(fetch,enumerate(batches)):print(result,flush=True)
print('625 chars + variants:',len(titles),flush=True)

# Official Japanese old forms which KANJIDIC variant fields may not enumerate.
known={v['title'] for f in out.glob('wikt-batch-*.json') for v in json.loads(f.read_text())['query']['pages'].values()}
old=[]
for line in (out/'Unihan_Variants.txt').read_text().splitlines():
 if not line or line.startswith('#'):continue
 cp,typ,val=line.split('\t')
 if chr(int(cp[2:],16)) in chars and typ=='kJapaneseOldVariant':old.extend(chr(int(v[2:],16)) for v in val.split())
missing=sorted(set(old)-known)
if missing:
 q={'action':'query','prop':'revisions','rvprop':'ids|timestamp|content','rvslots':'main','titles':'|'.join(missing),'format':'json'}
 req=urllib.request.Request('https://ko.wiktionary.org/w/api.php?'+urllib.parse.urlencode(q),headers={'User-Agent':'JapaneseGrammarGarden/0.3.8 (https://github.com/phone73-cmd/japanese-grammar-garden)'})
 (out/'wikt-batch-variants.json').write_bytes(urllib.request.urlopen(req,timeout=40).read())
