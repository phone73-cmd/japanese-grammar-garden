/* Additive curriculum: old questions keep their lesson ID and array index. */
window.JGG_COURSE = (()=>{
 const data=window.JGG_COURSE_DATA;
 const shuffle=a=>{const b=a.slice();for(let i=b.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[b[i],b[j]]=[b[j],b[i]]}return b};
 const question=(prompt,answer,wrong,reason,meta={})=>{const choices=shuffle([answer,...new Set(wrong.filter(x=>x!==answer))].slice(0,4));if(choices.length!==4)return null;return {question:prompt,choices,correct:choices.indexOf(answer),reason,...meta}};
 function extend(content){
  for(let n=1;n<=60;n++){
   const d=content[n],add=data.lessons[n];d.legacyCount=d.questions.length;
   // Do not shuffle during loading: appended indices must survive reload and backups.
   const append=q=>{if(q)d.questions.push(q)};
   if(add){
    for(const q of add.questions)append({...q,choices:q.choices.slice()});
    const targets=[6,8,41,42,43].includes(n)?[]:data.targets[n]||[];
    for(const e of d.examples){const target=targets.find(t=>e[0].includes(t));if(!target)continue;
     const other=[...targets,...['に','を','で','の','が','ます','です','ない','た']].filter(x=>x!==target);
     const choices=[target,...new Set(other)].slice(0,4);
     append({question:`빈칸 · ${e[3]}\n${e[0].replace(target,'＿＿')}`,choices,correct:0,reason:`${e[0]} → ${e[3]} ${add.tip}`,skill:'빈칸'});
    }
    // Dedicated judgements, rather than random claims attached to the old ten items.
    for(const [i,q] of add.questions.entries()){
     const falseClaim=i%2===1,claim=q.choices[falseClaim?1:q.correct];
     append({question:`판단 · ${q.question}\n제시: ${claim}`,choices:['O · 맞아요','X · 아니에요','판단 보류','해당 없음'],correct:falseClaim?1:0,reason:q.reason,skill:'문법 판단',judgement:true});
    }

   }
   const rows=data.kana[n]||[];
   for(const [rowIndex,row] of rows.entries()){
    // Same-sound glyphs are excluded from reverse-question distractors.
    const groups=[["ぬ","め"],["れ","ね","わ"],["る","ろ"],["シ","ツ"],["ソ","ン"],["ク","ケ"],["フ","ワ"],["ア","マ"]],similar=groups.find(g=>g.includes(row.glyph))||[];const wrong=rows.slice(rowIndex+1).concat(rows.slice(0,rowIndex)).filter(x=>x.romaji!==row.romaji).sort((a,b)=>Number(similar.includes(b.glyph))-Number(similar.includes(a.glyph)));
    const romaji=[...new Set(wrong.map(x=>x.romaji))].slice(0,3);
    append({question:`「${row.glyph}」의 기본 소리는?`,choices:[row.romaji,...romaji],correct:0,reason:`${row.glyph} → ${row.romaji}. ${row.group}. 로마자는 보조 표기입니다.`,skill:'문자 읽기',kanaKey:row.key});
    const glyphs=wrong.map(x=>x.glyph).slice(0,3);
    append({question:`${row.romaji} 소리에 해당하는 ${n<4?'히라가나':'가타카나'}는?`,choices:[row.glyph,...glyphs],correct:0,reason:`${row.glyph} → ${row.romaji}. ${row.group}.`,skill:'문자 구별',kanaKey:row.key});
   }
   for(let i=d.legacyCount;i<d.questions.length;i++){const q=d.questions[i];if(q.judgement)continue;const shift=i%4;q.choices=q.choices.slice(shift).concat(q.choices.slice(0,shift));q.correct=(q.correct-shift+4)%4}
  }
 }
 function cleanProgress(raw){const result={};if(raw&&typeof raw==='object'&&!Array.isArray(raw))for(const [key,value] of Object.entries(raw))if(/^([1-9]|[1-5][0-9]|60)$/.test(key)&&Array.isArray(value))result[key]=[...new Set(value.filter(x=>typeof x==='string'&&x.length<100))].slice(0,200);return result}
 function cleanKana(raw){const keys=new Set(Object.values(data.kana).flat().map(x=>x.key)),out={};if(raw&&typeof raw==='object')for(const [key,v] of Object.entries(raw))if(keys.has(key)&&v&&typeof v==='object')out[key]={seen:Math.max(0,Math.min(100000,Number.isFinite(v.seen)?v.seen:0)),correct:Math.max(0,Math.min(100000,Number.isFinite(v.correct)?v.correct:0))};return out}
 return {data,shuffle,extend,cleanProgress,cleanKana};
})();
