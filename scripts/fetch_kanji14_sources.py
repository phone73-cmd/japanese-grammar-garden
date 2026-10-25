"""Fetch source snapshots for the 14-card/index build; keep existing inputs unchanged.
Usage: python scripts/fetch_kanji14_sources.py /path/to/dictionaries
Raw downloads stay outside the public repository.
"""
import sys,json,hashlib,urllib.request,urllib.parse,zipfile
from pathlib import Path
D=Path(sys.argv[1]);D.mkdir(parents=True,exist_ok=True)
headers={'User-Agent':'JapaneseGrammarGarden/0.3.11 (dictionary evidence; https://github.com/phone73-cmd/japanese-grammar-garden)'}
def fetch(path,url):
 if not path.exists():
  req=urllib.request.Request(url,headers=headers)
  with urllib.request.urlopen(req,timeout=60) as r:path.write_bytes(r.read())
 print(path.name,hashlib.sha256(path.read_bytes()).hexdigest())
fetch(D/'kanjidic2.xml.gz','https://www.edrdg.org/kanjidic/kanjidic2.xml.gz')
fetch(D/'JMdict_e.gz','https://www.edrdg.org/pub/Nihongo/JMdict_e.gz')
if not (D/'Unihan_Variants.txt').exists():
 fetch(D/'Unihan.zip','https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip')
 with zipfile.ZipFile(D/'Unihan.zip') as z:(D/'Unihan_Variants.txt').write_bytes(z.read('Unihan_Variants.txt'))
q={'action':'query','prop':'revisions','rvprop':'ids|timestamp|content','rvslots':'main','titles':'並|券|召|届|探|滞|看|航|袋|許|護|販|軽|辛|屆|滯|輕','format':'json'}
fetch(D/'wikt-new14.json','https://ko.wiktionary.org/w/api.php?'+urllib.parse.urlencode(q))
assert 'query' in json.loads((D/'wikt-new14.json').read_text()),'No dictionary pages in API response'
