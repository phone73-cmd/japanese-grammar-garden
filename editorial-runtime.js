/* Apply reviewed text revisions without changing lesson/question/example indices. */
window.JGG_EDITORIAL=(()=>{
 const data=window.JGG_EDITORIAL_DATA,oldQuestions=new Map(),originalQuestions=new Map(),oldExamples=new Map();let stats=null;
 const clone=x=>JSON.parse(JSON.stringify(x));
 function apply(content,practice,course){
  if(stats)return stats;
  const mappings=new Map(data.patches.map(p=>[p.before[0],p.after])),tokens=new Map();
  for(const p of data.patches)for(const i of [0,1,3])if(p.before[i]!==p.after[i]){
   if(tokens.has(p.before[i])&&tokens.get(p.before[i])!==p.after[i])throw Error('conflicting editorial mapping');tokens.set(p.before[i],p.after[i]);
  }
  const escape=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),pattern=new RegExp([...tokens.keys()].sort((a,b)=>b.length-a.length).map(escape).join('|'),'g'),replace=s=>s.replace(pattern,part=>tokens.get(part));
  stats={version:data.version,mappings:data.patches.length,examples:0,questions:0,practiceRows:0,correctedGaps:0};
  for(const [id,d]of Object.entries(content)){
   d.examples=d.examples.map((e,i)=>{const next=mappings.get(e[0]);if(!next)return e;oldExamples.set(id+':'+i,e.slice());stats.examples++;return next.slice()});
   d.questions=d.questions.map((q,i)=>{const next={...q,question:replace(q.question),choices:q.choices.map(replace),reason:replace(q.reason)};
    if(id==='25'&&[12,13,14].includes(i)){
     const correct=next.choices[next.correct],alternative=correct==='に'?'へ':'に';if(!['に','へ'].includes(correct)||!next.choices.includes(alternative))throw Error('editorial gap source changed');
     const legacy=clone(q);legacy.acceptedAnswers=[q.correct,q.choices.indexOf(alternative)];legacy.reason+=' 목적지에는 に와 へ를 모두 사용할 수 있습니다.';oldQuestions.set(id+':'+i,legacy);
     next.choices=next.choices.map(x=>x===alternative?'の':x);next.reason+=' 목적지에는 に와 へ를 모두 사용할 수 있습니다.';stats.correctedGaps++;
    }
    if(JSON.stringify(next)!==JSON.stringify(q)){originalQuestions.set(id+':'+i,clone(q));if(!oldQuestions.has(id+':'+i))oldQuestions.set(id+':'+i,clone(q));stats.questions++}return next;
   });
  }
  for(const d of Object.values(practice.lessons))for(const field of ['examples','assessments'])d[field]=d[field].map(e=>{const next=mappings.get(e[0]);if(next){stats.practiceRows++;return next.slice()}return e});
  const tips={28:'이동 동사의 ています는 문맥에 따라 결과 상태나 반복도 나타냅니다. 이동 중임을 분명히 말할 때는 向かっています처럼 표현할 수 있습니다.',34:'금지를 말하는 학교·시설 규칙의 예문입니다. 단순 부정 ません과 구분하고 상황에 맞게 말하세요.',45:'평범한 행동만 나열하기보다 무엇을 어디에서 경험했는지 드러내세요. 특정 장소·대상과 함께 경험을 말하는 연습을 합니다.',49:'伺う는 방문하는 상대를 높이는 겸양어입니다. 장소에 가는 것을 언제나 伺う로 바꾸지는 않습니다.',58:'운영 시간을 물을 때는 입장·체크인·창구 등 무엇의 시간인지 분명하게 말합니다.',59:'분실한 사람과 분실물을 발견한 사람의 말을 구분하세요. 届ける는 맡기거나 전달하는 뜻입니다.'};
  for(const [id,text]of Object.entries(tips))course.lessons[id].tip+=' '+text;
  return stats;
 }
 return {version:data.version,apply,originalQuestion:(id,i)=>originalQuestions.get(id+':'+i),legacyQuestion:(id,i)=>oldQuestions.get(id+':'+i),legacyExample:(id,i)=>oldExamples.get(id+':'+i),get stats(){return stats}};
})();
