"""Build supplemental cards from existing example sentences; never renumber core items."""
from pathlib import Path
import json,subprocess,gzip,xml.etree.ElementTree as ET,hashlib,sys
root=Path(__file__).resolve().parents[1]
core=[x for n in range(1,6) for x in json.loads((root/f'data/kanji/kanji-stage-{n}-100.draft.json').read_text())['items']]
js="const fs=require('fs'),vm=require('vm');let c={window:{}};vm.createContext(c);vm.runInContext(fs.readFileSync('grammar-lessons.js','utf8'),c);const h=fs.readFileSync('index.html','utf8');vm.runInContext(h.slice(h.indexOf('const makeQ='),h.indexOf('\\nlet state='))+';globalThis.lessons=content;',c);console.log(JSON.stringify(c.lessons));"
grammar=json.loads(subprocess.run(['node','-e',js],cwd=root,check=True,capture_output=True,text=True).stdout)
sentences=[{'ja':e[0],'reading':e[1],'translation_ko':e[3],'source':f'grammar-lesson-{n}'} for n,d in grammar.items() for e in d['examples']]+[{**x['example_sentence'],'source':x['id']} for x in core]
core_chars={x['character'] for x in core}
missing={c for e in sentences for c in e['ja'] if '\u4e00'<=c<='\u9fff'}-core_chars
rows=[line.split('|') for line in (root/'data/kanji/extra-words.tsv').read_text().splitlines() if line]
assert len(rows)==125 and len({r[0] for r in rows})==125 and {r[0] for r in rows}==missing
pairs={(r[2],r[3]):[] for r in rows};dictionary=Path(sys.argv[1]);digest=hashlib.sha256(dictionary.read_bytes()).hexdigest()
with gzip.open(dictionary,'rb') as f:
 for _,e in ET.iterparse(f,events=['end']):
  if e.tag!='entry':continue
  forms={k.text for k in e.findall('./k_ele/keb')}
  for r in e.findall('r_ele'):
   reading=r.findtext('reb');restrict={x.text for x in r.findall('re_restr')}
   for form in forms:
    if (form,reading) in pairs and (not restrict or form in restrict):pairs[form,reading].append(e.findtext('ent_seq'))
  e.clear()
items=[]
for order,(ch,meaning,word,reading,ko) in enumerate(rows,1):
 evidence=pairs[word,reading];sentence=next(e for e in sentences if ch in e['ja'])
 items.append({'id':f'extra-{ord(ch):04x}','character':ch,'stage':6,'order':order,'group_name':'문장 속 추가 한자','meaning_ko':meaning,'example_words':[{'word':word,'reading':reading,'meaning_ko':ko,'dictionary_reading_match':bool(evidence),'dictionary_entry_sequences':evidence,'reading_editorial_review_required':not bool(evidence)}],'example_sentence':sentence,'editorial_status':'authored_draft','source':'existing-app-sentence-and-authored-korean-gloss'})
payload={'schema_version':'kanji-v1','version':'0.3.5-dev','status':'supplemental-draft','count':125,'dictionary':{'url':'https://www.edrdg.org/pub/Nihongo/JMdict_e.gz','sha256':digest,'matched':sum(x['example_words'][0]['dictionary_reading_match'] for x in items),'total':125},'items':items}
(root/'data/kanji/kanji-extra-125.draft.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'count':len(items),'dictionary_matched':payload['dictionary']['matched'],'unmatched':[list(p) for p,v in pairs.items() if not v]},ensure_ascii=False))
