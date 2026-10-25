/* Stable additive examples/questions and per-record exposure rotation. */
window.JGG_PRACTICE=(()=>{
 const data=window.JGG_PRACTICE_DATA,families=new Map();
 const canon=s=>s.replace(/[\s。、「」『』！？?!]/g,'');
 function family(id,index,content){return families.get(id+':'+index)||id+':legacy:'+index}
 function extend(content){for(let id=1;id<=60;id++){
  const d=content[id],add=data.lessons[id];d.v039Count=d.questions.length;d.v039ExampleCount=d.examples.length;
  // Map old directions/gaps to one source example without mutating old question objects.
  d.questions.forEach((q,i)=>{const correct=q.choices[q.correct],ex=d.examples.find(e=>correct===e[0]||correct===e[3]||q.question.includes(e[0])||q.reason.startsWith(e[0]+' →'));
   const kana=(window.JGG_COURSE.data.kana[id]||[]).find(row=>q.kanaKey===row.key||q.question.includes('‘'+row.glyph+'’')||q.question.includes('「'+row.glyph+'」'));const source=kana?'kana:'+kana.key:ex?'text:'+canon(ex[0]):'rule:'+canon(q.reason);
   families.set(id+':'+i,id+':'+source);
  });
  for(const e of add.examples)if(!d.examples.some(old=>old[0]===e[0]))d.examples.push(e.slice());
  const rows=add.assessments;
  rows.forEach((e,i)=>{
   // All distractors come from distinct attested/authored contexts and meanings.
   for(const [mode,field,skill] of [['meaning',3,'상황 이해'],['sentence',0,'문형·활용'],['reading',1,'문장 읽기']]){
    const target=e[field],wrong=[...new Set(rows.slice(i+1).concat(rows.slice(0,i)).map(r=>r[field]).filter(x=>x!==target))].slice(0,3);if(wrong.length!==3)throw Error('insufficient distinct choices');
    const shift=(i+field)%4,choices=[target,...wrong];const ordered=choices.slice(shift).concat(choices.slice(0,shift));
    const question=mode==='meaning'?`상황 이해 · 「${e[0]}」의 뜻은?`:mode==='sentence'?`문형 적용 · “${e[3]}”에 맞는 표현은?`:`문장 읽기 · 「${e[0]}」의 읽기는?`;
    const index=d.questions.length;d.questions.push({question,choices:ordered,correct:(4-shift)%4,reason:`${e[0]} (${e[1]}) → ${e[3]}`,skill});families.set(id+':'+index,id+':text:'+canon(e[0]));
   }
   if(add.mora){const count=Array.from(e[1]).filter(c=>!('ゃゅょぁぃぅぇぉ'.includes(c))&&/[ぁ-ゖー]/.test(c)).length,others=[count+1,count+2,count===1?4:count-1];const index=d.questions.length;d.questions.push({question:`「${e[0]}」는 몇 박자인가요?`,choices:[count,...others].map(n=>n+'박자'),correct:0,reason:`${e[1]}는 ${count}박자입니다. 작은 요음은 앞 글자와 한 박자, っ·ん·장음은 각각 한 박자로 셉니다.`,skill:'박자'});families.set(id+':'+index,id+':text:'+canon(e[0]));}
  });
 }window.JGG_EDITORIAL?.apply(content,data,window.JGG_COURSE.data);}
 function clean(raw,content){const out={round:0,shown:{},families:{}};if(!raw||typeof raw!=='object')return out;out.round=Number.isSafeInteger(raw.round)&&raw.round>=0?Math.min(raw.round,10000000):0;const allowed=new Set(families.values());for(const [key,value] of Object.entries(raw.shown||{})){const [id,index]=key.split(':').map(Number);if(/^\d+:\d+$/.test(key)&&content[id]?.questions[index]&&Number.isSafeInteger(value)&&value>=0&&value<=out.round)out.shown[key]=value}for(const [key,value] of Object.entries(raw.families||{}))if(allowed.has(key)&&Number.isSafeInteger(value)&&value>=0&&value<=out.round)out.families[key]=value;for(const [key,value] of Object.entries(out.shown)){const [id,index]=key.split(':').map(Number),f=family(id,index,content);out.families[f]=Math.max(out.families[f]||0,value)}return out}
 function select(content,record,id,format,shuffle,due){
  const history=clean(record.practiceHistory,content),ids=id%10===0?Array.from({length:9},(_,i)=>id-9+i):[id],pool=[];
  for(const n of ids)content[n].questions.forEach((q,index)=>{if(format==='ox'||!q.judgement)pool.push({lessonId:n,questionIndex:index})});
  const errors=new Set(record.review.filter(r=>!r.resolved).map(r=>r.lessonId+':'+r.questionIndex));
  const ranked=shuffle(pool).sort((a,b)=>{
   const ak=a.lessonId+':'+a.questionIndex,bk=b.lessonId+':'+b.questionIndex,af=family(a.lessonId,a.questionIndex,content),bf=family(b.lessonId,b.questionIndex,content);
   const fresh=r=>{const key=r.lessonId+':'+r.questionIndex;return errors.has(key)?3:!record.reviewSchedule?.[key]?2:due(record.reviewSchedule[key].dueAt)?1:0};
   // Age takes precedence over error/type preference in regular practice.
   return (history.families[af]||0)-(history.families[bf]||0)||(history.shown[ak]||0)-(history.shown[bk]||0)||(format==='ox'?Number(!!content[b.lessonId].questions[b.questionIndex].judgement)-Number(!!content[a.lessonId].questions[a.questionIndex].judgement):0)||fresh(b)-fresh(a);
  });
  const group=r=>family(r.lessonId,r.questionIndex,content).replace(/^\d+:/,'');const picked=[],used=new Set();const take=r=>{if(!r)return false;const f=group(r);if(used.has(f))return false;used.add(f);picked.push(r);return true};
  if(ids.length>1)for(const n of ids)take(ranked.find(r=>r.lessonId===n&&!used.has(group(r))));
  for(const r of ranked){if(picked.length===10)break;take(r)}
  if(picked.length!==10)throw Error('ten distinct content families required');return shuffle(picked);
 }
 function remember(record,refs,content){const h=clean(record.practiceHistory,content);h.round++;for(const r of refs){h.shown[r.lessonId+':'+r.questionIndex]=h.round;h.families[family(r.lessonId,r.questionIndex,content)]=h.round}record.practiceHistory=h}
 return {data,extend,family,clean,select,remember};
})();
