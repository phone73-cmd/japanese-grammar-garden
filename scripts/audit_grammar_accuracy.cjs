/* Read-only content audit. Does not rewrite app content or learning records. */
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),crypto=require('node:crypto');
process.chdir(path.join(__dirname,'..'));
const files=['index.html','grammar-lessons.js','course-data.js','course-runtime.js','practice-data.js','editorial-data.js','editorial-runtime.js','practice-runtime.js'];
const html=fs.readFileSync('index.html','utf8'),ctx={window:{}};vm.createContext(ctx);
for(const p of files.slice(1))vm.runInContext(fs.readFileSync(p,'utf8'),ctx);
vm.runInContext(html.slice(html.indexOf('const makeQ='),html.indexOf('\nlet state='))+';window.auditContent=content',ctx);
const content=ctx.window.auditContent,course=ctx.window.JGG_COURSE_DATA,practice=ctx.window.JGG_PRACTICE_DATA;
const invalid=[],ambiguous=[];let examples=0,questions=0,judgements=0,gaps=0,dialogueTurns=0,assessments=0;
for(const [id,d] of Object.entries(content)){
 for(const [i,e]of d.examples.entries()){examples++;if(e.length!==4||!e.every(s=>typeof s==='string'&&s.trim()))invalid.push({lesson:+id,exampleIndex:i,type:'example_fields'})}
 for(const [i,q]of d.questions.entries()){
  questions++;if(q.judgement)judgements++;if(q.question.includes('＿＿'))gaps++;
  if(q.choices.length!==4||new Set(q.choices).size!==4||!Number.isInteger(q.correct)||!q.choices[q.correct]||!q.reason)invalid.push({lesson:+id,questionIndex:i,type:'question_structure'});
  if(!q.judgement&&['に','へ'].includes(q.choices[q.correct])&&q.question.includes('＿＿')&&q.choices.includes('に')&&q.choices.includes('へ')&&/＿＿(?:行き|帰り|来)/.test(q.question))ambiguous.push({lesson:+id,questionIndex:i,question:q.question,choices:q.choices,markedCorrect:q.choices[q.correct],alsoAcceptable:q.choices[q.correct]==='に'?'へ':'に',severity:'confirmed_multiple_valid_answers',source:'JF-IRODORI-A1-L18-p17'});
 }
 assessments+=practice.lessons[id].assessments.length;
 dialogueTurns+=(course.lessons[id]?.dialogue||[]).length+(practice.lessons[id].dialogues||[]).reduce((s,a)=>s+a.length,0);
}
const oxConstructionConflicts=[];for(const [id,d]of Object.entries(course.lessons))for(const [i,q]of d.questions.entries())if(i%2===1&&q.correct===1)oxConstructionConflicts.push({lesson:+id,sourceQuestionIndex:i});
const output={base_version:'0.3.12-dev',tested_version:'0.3.13-dev',base_commit:'acb545a7578f6ce9340988c780b456c5ff4ca580',date:'2026-10-25',hashes:Object.fromEntries(files.map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')])),scope:{lessons:60,examples,questions,assessmentContexts:assessments,dialogueTurns,judgements,gaps},editorialStats:ctx.window.JGG_EDITORIAL.stats,structuralIssues:invalid,oxConstructionConflicts,confirmedAmbiguousQuestions:ambiguous,status:'editorial_corrections_applied_not_native_certification',limitations:['Structural checks do not prove semantic correctness or unique answers.','717 learning examples and 108 dialogue turns received a first-pass model editorial review, not native certification.','1828 assessment contexts reviewed through generator rules, inflection/slot tables and targeted high-risk rows; full independent sentence-by-sentence semantic certification incomplete.','Kanji 639 complete source re-audit and accent/audio verification are outside this grammar-focused pass.'],deviceValidation:{status:'user_reported_complete',date:'2026-10-25',independent_retest:false,device_browser_cases_not_individually_recorded:true}};
fs.writeFileSync('data/grammar/ACCURACY-AUDIT-v0.3.13.json',JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({scope:output.scope,editorial:output.editorialStats,structuralIssues:invalid.length,oxConstructionConflicts:oxConstructionConflicts.length,confirmedAmbiguousQuestions:ambiguous},null,2));
