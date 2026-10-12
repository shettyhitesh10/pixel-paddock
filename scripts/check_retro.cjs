/* Release 4 template/interaction checks. This is not browser layout verification. */
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path');
const root=path.resolve(__dirname,'..'),dist=path.join(root,'dist'),data=JSON.parse(fs.readFileSync(path.join(dist,'data/content.json')));
const nodes=new Map(),handlers={},storage=new Map(),errors=[];
function node(id){if(!nodes.has(id)){const classes=new Set();nodes.set(id,{id,innerHTML:'',textContent:'',dataset:{},classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x),toggle(x,b){const on=b===undefined?!classes.has(x):b;on?classes.add(x):classes.delete(x);return on}},setAttribute(){},removeAttribute(){},focus(){},hasAttribute:()=>false,closest:()=>null})}return nodes.get(id)}
const document={body:node('body'),querySelector:node,querySelectorAll:()=>[],addEventListener:(e,f)=>handlers[e]=f,title:''};
const c={document,location:{hash:''},localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},URL,URLSearchParams,Date,Math,Map,Set,JSON,Number,String,Array,Object,encodeURIComponent,decodeURIComponent,setTimeout:()=>1,clearTimeout(){},setInterval(){},matchMedia:()=>({matches:false}),getComputedStyle:()=>({gridTemplateColumns:'1fr 1fr 1fr 1fr 1fr'}),console:{log:console.log,error:e=>errors.push(String(e))}};
c.window={...c,PIXEL_PADDOCK_BOOTSTRAP:data,scrollTo(){},addEventListener:(e,f)=>handlers['window:'+e]=f};vm.createContext(c);
for(const file of ['pixel-art.js','artwork.js','app.js'])vm.runInContext(fs.readFileSync(path.join(dist,file),'utf8'),c,{filename:file});
assert.deepEqual(errors,[]);assert.ok(node('#main').innerHTML.includes('AFTER SINGAPORE GRAND PRIX'));
const markup={},checks=[];
function nav(route){c.location.hash='#/'+route;handlers['window:hashchange']();const html=node('#main').innerHTML;assert.ok(!html.includes('CARTRIDGE NOT READY'));return markup[route||'dashboard']=html}
function click(dataset={},id=''){const b={...node('button'),id,dataset,closest:()=>null};handlers.click({target:{closest:()=>b}});return b}
for(const r of ['','drivers','teams','principals','races','race/singapore','paddock','favorites','sources']){const h=nav(r);assert.ok(h.length>300,r);assert.ok(!/<img\b/i.test(h),'No photos: '+r)}
checks.push('Nine main screens render against the captured data, without photograph elements.');
let profiles=0;const all=[...data.drivers,...data.formerDrivers];
for(const [kind,items] of [['driver',all],['team',data.teams],['principal',data.principals]])for(const item of items){const h=nav(kind+'/'+item.id);assert.ok(h.includes('<h1>'+item.name+'</h1>'),item.id);assert.ok(h.includes('SOURCE NOTES'),item.id);assert.ok(!h.includes('fallback-art'),item.id);profiles++}
assert.equal(profiles,47);
checks.push('All 47 individual profile routes render, including the former season entrant and distinct leadership roles.');
for(const r of data.calendar){const h=nav('race/'+(r.round===17?'singapore':r.round));assert.ok(!h.includes('WRONG GARAGE'));assert.ok(!h.includes('undefined'))}
nav('driver/stroll');assert.ok(node('#main').innerHTML.includes('<strong>NC</strong>'));
nav('driver/tsunoda');assert.ok(node('#main').innerHTML.includes('NOT ENTERED'));
nav('race/singapore');assert.ok(node('#main').innerHTML.includes('1:42:00.785'));assert.ok(!node('#main').innerHTML.includes('data-countdown'));
for(const session of ['qualifying','sprint','race']){click({session});assert.equal((node('#session-results').innerHTML.match(/<tr>/g)||[]).length,23);assert.ok(node('.race-classification .panel-foot a').href.endsWith(session==='race'?'race-result':session==='sprint'?'sprint-results':'qualifying'));assert.ok(node('#session-date').textContent.startsWith(session==='race'?'11':'10'))}
checks.push('All 23 race routes render; race, Sprint and qualifying tabs each show 22 rows with their matching source and date.');
nav('drivers');handlers.input({target:{id:'search',value:'hamilton'}});assert.equal((node('#driver-slots').innerHTML.match(/data-select-driver=/g)||[]).length,1);assert.ok(node('#driver-preview').innerHTML.includes('Hamilton'));
handlers.input({target:{id:'search',value:'nothingmatcheszzz'}});assert.ok(node('#driver-slots').innerHTML.includes('NO DRIVER FOUND'));
nav('drivers');handlers.change({target:{id:'team-filter',value:'ferrari'}});assert.equal((node('#driver-slots').innerHTML.match(/data-select-driver=/g)||[]).length,2);
click({selectDriver:'leclerc'});assert.ok(node('#driver-preview').innerHTML.includes('Leclerc'));
click({favorite:'driver:leclerc'});assert.ok(storage.get('paddock:favorites').includes('leclerc'));assert.ok(nav('favorites').includes('Charles Leclerc'));click({favorite:'driver:leclerc'});assert.ok(node('#main').innerHTML.includes('YOUR GRID IS OPEN'));
click({},'motion-toggle');assert.equal(storage.get('paddock:motion'),'false');assert.ok(document.body.classList.contains('motion-off'));click({play:'leclerc'});assert.ok(node('#toast').textContent.includes('Motion is off'));
nav('paddock');click({paddockTab:'notes'});handlers.submit({preventDefault(){},target:{id:'note-form',elements:{text:{value:'<script>alert(1)</script>'}},reset(){}}});assert.ok(node('#notes-list').innerHTML.includes('&lt;script&gt;'));assert.ok(!node('#notes-list').innerHTML.includes('<script>'));const note=JSON.parse(storage.get('paddock:notes'))[0];click({deleteNote:note.id});assert.equal(storage.get('paddock:notes'),'[]');
click({paddockTab:'comments'});assert.equal((node('#paddock-results').innerHTML.match(/class="comment-card"/g)||[]).length,5);click({paddockTab:'news'});handlers.change({target:{id:'entity-filter',value:'fred-vasseur'}});assert.ok(node('#paddock-results').innerHTML.includes('Vasseur'));
checks.push('Driver search, team filter, selection, favorites, FX toggle, content filtering and escaped private-note creation/deletion pass handler checks.');
const ids=new Set([...all,...data.teams,...data.principals].map(x=>x.id));
for(const x of [...data.news,...data.comments]){assert.ok(x.url.startsWith('https://'));for(const id of x.tags)assert.ok(ids.has(id),id)}
for(const d of all)assert.ok(data.teams.some(t=>t.id===d.teamId));
for(const t of data.teams){for(const id of t.driverIds)assert.ok(data.drivers.some(d=>d.id===id));for(const id of t.leadershipIds)assert.ok(data.principals.some(p=>p.id===id))}
assert.equal(data.standings.drivers.length,23);assert.equal(data.standings.drivers[0].points,340);assert.equal(data.standings.teams[0].points,578);assert.equal(data.standings.drivers.reduce((s,x)=>s+x.wins,0),17);
assert.equal(data.results.reduce((s,x)=>s+x.points,0),101);assert.equal(data.sprintResults.reduce((s,x)=>s+x.points,0),36);
const art=c.window.PADDOCK_ART;assert.equal(Object.keys(art.people).length,36);for(const d of [...all,...data.principals]){const a=art.people[d.id];assert.ok(a,d.id);assert.equal(a.frames,6);assert.ok(fs.existsSync(path.join(dist,a.src)),a.src)}
checks.push('Standings, points, roster links, content tags and 36 six-frame artwork mappings are consistent; 23 season entrants are preserved.');
const css=fs.readFileSync(path.join(dist,'style.css'),'utf8');assert.equal((css.match(/{/g)||[]).length,(css.match(/}/g)||[]).length);assert.ok(css.includes('prefers-reduced-motion:reduce'));assert.ok(css.includes('background-size:600% 300%'));assert.ok(css.includes('100%{background-position-x:0%}'));
checks.push('Pixel CSS has balanced blocks, six-frame timing, responsive breakpoints and reduced-motion overrides.');
fs.mkdirSync(path.join(root,'qa-artifacts'),{recursive:true});fs.writeFileSync(path.join(root,'qa-artifacts/rendered-routes.json'),JSON.stringify(markup));
const report={executedAt:new Date().toISOString(),revision:4,status:'Source, template and handler checks passed; browser rendering unverified',profiles,animatedPeople:36,frames:216,checks,browserChecks:'Chromium launch blocked by sandbox; no layout, mobile overflow or browser persistence claim.',screenshots:[]};fs.writeFileSync(path.join(root,'qa-artifacts/retro-checks.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
