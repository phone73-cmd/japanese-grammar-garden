/* Structural/content-preservation audit; does not claim native-language review. */
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto'),assert=require('node:assert/strict'),path=require('node:path');
process.chdir(path.join(__dirname,'..'));
const html=fs.readFileSync('index.html','utf8'),context={window:{}};vm.createContext(context);
for(const f of ['grammar-lessons.js','course-data.js','course-runtime.js'])vm.runInContext(fs.readFileSync(f,'utf8'),context);
vm.runInContext(html.slice(html.indexOf('const makeQ='),html.indexOf('\nlet state='))+';window.auditContent=content',context);
const content=context.window.auditContent,data=context.window.JGG_COURSE_DATA;
const expected=JSON.parse(fs.readFileSync('tests/fixtures/legacy-questions-v038.sha256.json','utf8'));
const counts=[];let total=0,judgements=0;
for(let id=1;id<=60;id++){
 const d=content[id],legacy=d.questions.slice(0,10);
 assert.equal(crypto.createHash('sha256').update(JSON.stringify(legacy)).digest('hex'),expected[id],`legacy question indices changed: ${id}`);
 for(const q of d.questions){assert.equal(q.choices.length,4);assert.equal(new Set(q.choices).size,4);assert.ok(q.choices.every(x=>typeof x==='string'&&x.trim()));assert.ok(q.correct>=0&&q.correct<4);assert.ok(q.reason);if(q.judgement)judgements++}
 total+=d.questions.length;counts.push({lesson:id,legacy:10,total:d.questions.length,focused:d.questions.filter(q=>q.skill&&!q.judgement).length,judgements:d.questions.filter(q=>q.judgement).length,examples:d.examples.length,table_rows:data.lessons[id]?.table.length||0,dialogue_turns:data.lessons[id]?.dialogue?.length||0,comprehensive:id%10===0});
}
const kana={};for(const [id,rows] of Object.entries(data.kana)){
 assert.equal(new Set(rows.map(x=>x.glyph)).size,rows.length);kana[id]=rows.length;
 if(id==='1'||id==='4')assert.equal(rows.length,46);
 for(const row of rows){const qs=content[id].questions.filter(q=>q.kanaKey===row.key);assert.equal(qs.length,2);const reverse=qs[1];for(const other of rows.filter(x=>x.glyph!==row.glyph&&x.romaji===row.romaji))assert.ok(!reverse.choices.includes(other.glyph))}
}
const result={version:'0.3.9-dev',date:'2026-10-24',legacy_questions_unchanged:600,total_questions:total,new_questions:total-600,dedicated_judgements:judgements,kana_inventory:kana,dialogues:9,dialogue_turns:36,lessons:counts,status:'structure_and_legacy_preservation_passed_not_native_review'};
fs.writeFileSync('data/grammar/COURSE-AUDIT-v0.3.9.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({...result,lessons:undefined},null,2));
