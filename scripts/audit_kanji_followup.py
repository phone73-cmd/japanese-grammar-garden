"""Read-only KANJIDIC2 recheck of the published enrichment, with explicit editorial limits."""
import sys, json, gzip, hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict

root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1])
overlay=json.loads((root/'data/kanji/kanji-enrichment.json').read_text())
dictionary={}
with gzip.open(source,'rb') as f:
    for _,el in ET.iterparse(f,events=('end',)):
        if el.tag=='character':
            values=defaultdict(list)
            for r in el.findall('./reading_meaning/rmgroup/reading'):
                if r.text:values[r.get('r_type')].append(r.text)
            dictionary[el.findtext('literal')]=values
            el.clear()
errors=[];fallback=[];pairs=defaultdict(set);form_candidates=[]
items=overlay['items']
assert len(items)==len({x['id'] for x in items})==len({x['character'] for x in items})==625
for x in items:
    d=dictionary[x['character']]
    for key,typ in [('on','ja_on'),('kun','ja_kun')]:
        if set(x[key])!=set(d[typ]):errors.append([x['id'],key,x[key],d[typ]])
    if d['korean_h']:
        if set(x['korean_readings'])!=set(d['korean_h']):errors.append([x['id'],'korean_h'])
    else:fallback.append(dict(id=x['id'],character=x['character'],source=x['korean_readings_source']))
    for g in x['korean_glosses']:
        if not g.get('gloss') or not g.get('source',{}).get('url'):errors.append([x['id'],'gloss source'])
        if g.get('reading') not in x['korean_readings']:form_candidates.append(dict(id=x['id'],character=x['character'],gloss=g['gloss'],reading=g['reading'],dictionary_readings=x['korean_readings']))
    if len({w['word'] for w in x['words']})<2:errors.append([x['id'],'study words'])
    for w in x['words']:
        if not w.get('dictionary_reading_match') or not w.get('meaning_ko'):errors.append([x['id'],'word evidence',w.get('word')])
        pairs[(w['word'],w['reading'])].add(w['meaning_ko'])
assert not errors,errors
result=dict(version='0.3.9-dev',date='2026-10-24',checked=625,official_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),on_kun_mismatches=0,korean_reading_mismatches=0,korean_fallbacks=fallback,gloss_reading_difference_candidates=form_candidates,translation_variant_candidates=[dict(word=k[0],reading=k[1],meanings=sorted(v)) for k,v in pairs.items() if len(v)>1],original_data_modified=False,verified='dictionary_field_recomparison_and_evidence_presence',unverified=['Whole-set authoritative Korean dictionary cross-certification','Native-level Japanese sentence and Korean translation review','Real iPhone Safari/PWA and voice quality'])
(root/'data/kanji/FOLLOWUP-AUDIT-v0.3.9.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('625 dictionary rows rechecked; reading mismatches 0;',len(form_candidates),'gloss-reading candidates;',len(result['translation_variant_candidates']),'translation variants (not automatically errors)')
