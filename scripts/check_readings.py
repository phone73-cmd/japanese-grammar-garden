"""Cross-check existing readings against an externally downloaded JMdict_e.gz.
Usage: python scripts/check_readings.py /path/JMdict_e.gz
No dictionary definitions are copied; evidence records entry sequence IDs.
"""
import gzip,hashlib,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(__file__).resolve().parents[1]
qpath=root/'data/kanji/READING-REVIEW-QUEUE.json';q=json.loads(qpath.read_text())
allitems=[x for n in range(1,6) for x in json.loads((root/f'data/kanji/kanji-stage-{n}-100.draft.json').read_text())['items']]
pairs={(w['word'],w['reading']) for x in allitems for w in x['example_words']}
evidence={};data=Path(sys.argv[1]).read_bytes();header=gzip.decompress(data)[:10000].decode()
for event,entry in ET.iterparse(gzip.open(sys.argv[1]),events=('end',)):
 if entry.tag!='entry':continue
 forms=[e.text for e in entry.findall('k_ele/keb')]
 for reading in entry.findall('r_ele'):
  kana=reading.findtext('reb');restricted=[e.text for e in reading.findall('re_restr')]
  applicable=restricted or forms or [kana]
  for form in applicable:
   pair=(form,kana)
   if pair in pairs:
    evidence.setdefault(pair,[]).append({'entry_sequence':entry.findtext('ent_seq'),'word':form,'reading':kana,'reading_restrictions':restricted})
 entry.clear()
source={'title':'JMdict (English edition), EDRDG','download_url':'https://www.edrdg.org/pub/Nihongo/JMdict_e.gz','project_url':'https://www.edrdg.org/wiki/JMdict-EDICT_Dictionary_Project.html','licence_url':'https://www.edrdg.org/edrdg/licence.html','file_sha256':hashlib.sha256(data).hexdigest(),'checked_at':'2026-10-23','method':'Exact keb/reb match with re_restr restrictions; not a sentence or Korean-meaning certification.'}
matched=0
for x in q['items']:
 m=evidence.get((x['word'],x['reading']))
 if m:
  x['dictionary_evidence']={'source_id':'jmdict-official-2026-10-23','entries':m};x['review_status']='dictionary_pair_verified_context_review_pending';matched+=1
q['dictionary_sources']={'jmdict-official-2026-10-23':source};q['status']='dictionary_pairs_checked_context_review_pending';q['dictionary_pair_matches']=matched;q['dictionary_pair_unmatched']=len(q['items'])-matched
qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
for x in allitems:
 for w in x['example_words']:
  m=evidence.get((w['word'],w['reading']))
  if m:w['dictionary_reading_match']=True;w['dictionary_entry_sequences']=[z['entry_sequence'] for z in m]
for n in range(1,6):
 path=root/f'data/kanji/kanji-stage-{n}-100.draft.json';datafile=json.loads(path.read_text());datafile['items']=[x for x in allitems if x['stage']==n];datafile['dictionary_source']=source;path.write_text(json.dumps(datafile,ensure_ascii=False,indent=2)+'\n')
report={'source':source,'queued_pairs':len(q['items']),'queue_matched':matched,'queue_unmatched':[{'word':x['word'],'reading':x['reading']} for x in q['items'] if (x['word'],x['reading']) not in evidence], 'vocabulary_entries':sum(len(x['example_words']) for x in allitems),'vocabulary_entries_matched':sum((w['word'],w['reading']) in evidence for x in allitems for w in x['example_words']), 'all_vocabulary_unmatched':[{'id':x['id'],'word':w['word'],'reading':w['reading']} for x in allitems for w in x['example_words'] if (w['word'],w['reading']) not in evidence]}
(root/'data/kanji/DICTIONARY-CHECK-v0.3.0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
