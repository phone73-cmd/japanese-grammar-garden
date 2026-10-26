/* Offline search and evidence-based recommendations. No learning records are mutated here. */
window.JGG_LIBRARY=(()=>{
 const categories={all:'전체',noun:'명사',verb:'동사',i_adj:'い형용사',na_adj:'な형용사',pronoun:'대명사·지시어',particle:'조사',adverb:'부사',interrogative:'의문사',conjunction:'접속 표현',grammar:'문법·문형',counter:'수량·조수사',rentaishi:'연체사',greeting:'인사·관용',phrase:'회화·문장',kana:'문자',kanji:'한자',unclassified:'분류 확인 중'};
 const norm=s=>String(s||'').normalize('NFKC').toLowerCase().replace(/[ァ-ヶ]/g,c=>String.fromCharCode(c.charCodeAt(0)-96)).replace(/[\s.\-〜～·、。「」『』!?！？]/g,'');
 const japaneseSort=new Intl.Collator("ja"),idSort=new Intl.Collator();
 let cached=null,pending=null;
 async function load(){if(cached)return cached;if(pending)return pending;pending=fetch('./data/library-index.json').then(r=>{if(!r.ok)throw Error('검색 자료를 불러오지 못했습니다.');return r.json()}).then(d=>{if(d.schema!=='jgg-library-v1'||d.kanji_count!==639||!Array.isArray(d.entries)||new Set(d.entries.map(e=>e.id)).size!==d.entries.length)throw Error('검색 자료를 확인하지 못했습니다.');for(const e of d.entries){if(!e.id||!e.japanese||!e.meaning||!Array.isArray(e.categories)||!Array.isArray(e.keywords))throw Error('검색 항목 오류');e._fields=[e.japanese,e.reading,e.meaning,...e.keywords,...e.categories.map(c=>categories[c]||'')].map(norm);e._text=e._fields.join(' ')}d.byId=new Map(d.entries.map(e=>[e.id,e]));d.byKanji=new Map(d.entries.filter(e=>e.kind==='kanji').map(e=>[e.kanjiId,e]));cached=d;return d}).catch(e=>{pending=null;throw e});return pending}
 function search(d,query='',category='all',limit=40){const q=String(query).trim().slice(0,100),parts=q.split(/\s+/).map(norm).filter(Boolean),full=norm(q);const matches=[];
  for(const e of d.entries){if(category!=='all'&&!e.categories.includes(category))continue;const fields=e._fields||[e.japanese,e.reading,e.meaning,...e.keywords,...e.categories.map(c=>categories[c]||'')].map(norm),text=e._text||fields.join(' ');if(parts.some(p=>!text.includes(p)))continue;const score=full?(fields.slice(0,3).some(f=>f===full)?100:fields.slice(0,3).some(f=>f.startsWith(full))?60:fields.some(f=>f===full)?50:10):0;matches.push({entry:e,score})}
  matches.sort((a,b)=>b.score-a.score||japaneseSort.compare(a.entry.japanese,b.entry.japanese)||idSort.compare(a.entry.id,b.entry.id));return {total:matches.length,entries:matches.slice(0,Math.max(1,Math.min(limit,10000))).map(x=>x.entry)};
 }
 function visibleCategories(d){return Object.fromEntries(Object.entries(categories).filter(([id])=>id!=='unclassified'||Boolean(d?.entries.some(e=>e.categories.includes(id)))))}
 function cleanView(raw){return {query:typeof raw?.query==='string'?raw.query.slice(0,100):'',category:categories[raw?.category]?raw.category:'all',limit:Number.isInteger(raw?.limit)?Math.max(40,Math.min(raw.limit,10000)):40,scroll:Number.isFinite(raw?.scroll)?Math.max(0,Math.min(raw.scroll,100000)):0}}
 function recommendations(content,record,kanji,now=Date.now()){
  const result={grammar:[],kana:[],kanji:[],sampledAttempts:0};const end=new Date(now);end.setHours(23,59,59,999);const due=x=>Number.isFinite(Date.parse(x))&&Date.parse(x)<=end.getTime();
  const errors=new Set((record.review||[]).filter(e=>!e.resolved&&content[e.lessonId]?.questions[e.questionIndex]).map(e=>e.lessonId+':'+e.questionIndex));
  const stats=new Map(),errorCounts=new Map(),dueCounts=new Map();
  for(const a of record.attempts||[])if(content[a.lessonId]&&(!a.kind||['lesson','ox'].includes(a.kind))&&Number.isInteger(a.total)&&a.total>0&&Number.isInteger(a.correct)&&a.correct>=0&&a.correct<=a.total){const x=stats.get(a.lessonId)||{total:0,correct:0,count:0};x.total+=a.total;x.correct+=a.correct;x.count++;stats.set(a.lessonId,x)}
  for(const key of errors){const id=Number(key.split(':')[0]);errorCounts.set(id,(errorCounts.get(id)||0)+1)}
  for(const [key,x] of Object.entries(record.reviewSchedule||{}))if(due(x.dueAt)){const id=Number(key.split(':')[0]);dueCounts.set(id,(dueCounts.get(id)||0)+1)}
  for(const [id,d] of Object.entries(content)){
   const {total=0,correct=0,count=0}=stats.get(Number(id))||{};result.sampledAttempts+=count;
   const bad=errorCounts.get(Number(id))||0,scheduled=dueCounts.get(Number(id))||0;
   const accuracy=total>=10?Math.round(correct*100/total):null;
   if(bad||scheduled||accuracy!==null&&accuracy<80)result.grammar.push({lessonId:Number(id),samples:total,accuracy,errors:bad,due:scheduled,reason:bad?'오답 복습':scheduled?'오늘 복습':accuracy<80?'문형 다시 익히기':'학습 기록',priority:bad?3:scheduled?2:1});
  }
  const reviewedKana=new Map();for(const [key,value] of Object.entries(record.reviewSchedule||{})){const [id,index]=key.split(':').map(Number);const q=content[id]?.questions[index];if(!q)continue;let kana=q.kanaKey;
   if(!kana&&window.JGG_PRACTICE){const f=window.JGG_PRACTICE.family(id,index,content);const m=f.match(/^\d+:kana:(.+)$/);if(m)kana=m[1]}
   if(!kana)continue;const old=reviewedKana.get(kana)||{key:kana,lessonId:id,errors:0,due:false,reviewed:0,streak:Infinity};old.reviewed++;old.errors+=errors.has(key)?1:0;old.due=old.due||due(value.dueAt);old.streak=Math.min(old.streak,Number.isFinite(value.streak)?value.streak:0);reviewedKana.set(kana,old);
  }
  for(const x of reviewedKana.values())if(x.errors||x.due||x.streak<2)result.kana.push({...x,glyph:x.key.split(':').slice(1).join(':'),group:x.lessonId<=2?'히라가나':'가타카나',reason:x.errors?'틀린 글자':x.due?'오늘 복습':'한 번 더 연습',priority:x.errors?3:x.due?2:1});
  if(kanji){const unique=new Map();for(const e of kanji.errors||[])if(!e.resolved){const key=e.id+'|'+(e.quizType||'word')+'|'+e.word+'|'+e.reading;if(!unique.has(key))unique.set(key,e)}const byId=new Map();for(const e of unique.values())byId.set(e.id,(byId.get(e.id)||0)+1);
   const ids=new Set([...Object.keys(kanji.learned||{}),...byId.keys()]);for(const id of ids){const x=kanji.learned?.[id]||{},bad=byId.get(id)||0,scheduled=due(x.dueAt);if(bad||scheduled)result.kanji.push({kanjiId:id,errors:bad,due:scheduled,streak:Number.isFinite(x.correct)?x.correct:0,reason:bad?'한자 오답 복습':'오늘 복습',priority:bad?3:2})}
  }
  const unitAttempts=(record.attempts||[]).filter(a=>content[a.lessonId]&&(!a.kind||a.kind==='lesson')),passed=new Set(unitAttempts.filter(a=>Number.isFinite(a.score)&&a.score>=80).map(a=>a.lessonId)),recent=unitAttempts.at(-1)?.lessonId;const start=recent?(passed.has(recent)?recent+1:recent):1,order=Object.keys(content).map(Number).sort((a,b)=>a-b);result.nextLesson=order.filter(n=>n>=start).concat(order.filter(n=>n<start)).find(n=>!passed.has(n))||null;result.nextReason=!unitAttempts.length?'기록이 부족해 1단계부터 시작해요.':result.nextLesson===recent?'최근 학습한 단원을 이어서 익혀요.':result.nextLesson?'아직 시험을 통과하지 않은 다음 단원을 배워요.':'모든 단원 시험을 통과했습니다. 복습 일정에 맞춰 이어가세요.';
  for(const key of ['grammar','kana','kanji'])result[key].sort((a,b)=>b.priority-a.priority||b.errors-a.errors||(a.accuracy??100)-(b.accuracy??100));return result;
 }
 return {categories,visibleCategories,norm,load,search,cleanView,recommendations};
})();
