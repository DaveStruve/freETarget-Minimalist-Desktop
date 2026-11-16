const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const script=fs.readFileSync(path.join(__dirname,'../app/assets/desktop_bootstrap.js'),'utf8');
const origin='http://127.0.0.1:34567', events=[],writes=[],fetches=[];
let failure=null,revision=7;
const durable=new Map([['ft-theme','dark']]);
class XHR{
 open(method,url,async){assert.equal(method,'POST');assert.equal(url,'/desktop/store');assert.equal(async,false)}
 setRequestHeader(k,v){(this.headers??={})[k]=v}
 send(raw){
  assert.equal(this.headers['X-FT-Session'],'secret');const body=JSON.parse(raw);writes.push(body);
  if(failure==='offline')throw Error('offline');
  if(failure==='disk'){this.status=500;this.responseText=JSON.stringify({error:'Disk full'});return}
  if(failure==='invalid'){this.status=200;this.responseText='invalid';return}
  if(body.expected_revision!==revision){this.status=409;this.responseText=JSON.stringify({error:'Local data changed'});return}
  body.remove?durable.delete(body.key):durable.set(body.key,body.value);
  this.status=200;this.responseText=JSON.stringify({revision:++revision});
 }
}
const window={location:{href:origin+'/app/secret/'},dispatchEvent:e=>events.push(e),fetch:async(input,options)=>{fetches.push({input,options});return {ok:true,json:async()=>({saved:true})}}};
const ctx={window,XMLHttpRequest:XHR,URL,Headers,CustomEvent:class{constructor(type,opts){this.type=type;this.detail=opts.detail}}};
vm.createContext(ctx);
vm.runInContext(script.replace('/*__FT_DESKTOP_BOOT__*/',JSON.stringify({origin,token:'secret',revision,storage:Object.fromEntries(durable)})),ctx);
const storage=window.FTDesktopStorage;
assert.equal(storage.getItem('ft-theme'),'dark');assert.equal(storage.getItem('absent'),null);assert.equal(storage.length,1);
storage.setItem('ft-theme','dark');assert.equal(writes.length,0);
storage.setItem('ft-theme','light');assert.equal(storage.getItem('ft-theme'),'light');assert.equal(durable.get('ft-theme'),'light');assert.equal(window.FTDesktop.revision,8);
for(const kind of ['disk','offline','invalid']){
 failure=kind;assert.throws(()=>storage.setItem('ft-theme','lost-value'));assert.equal(storage.getItem('ft-theme'),'light');assert.equal(window.FTDesktop.revision,8);assert.equal(durable.get('ft-theme'),'light');
}
failure=null;revision++;
assert.throws(()=>storage.removeItem('ft-theme'),/changed/);assert.equal(storage.getItem('ft-theme'),'light');
revision=8;storage.removeItem('ft-theme');assert.equal(storage.getItem('ft-theme'),null);assert.equal(storage.length,0);assert.equal(storage.key(0),null);
assert.equal(events.length,4);assert.ok(events.every(e=>e.type==='ft-storage-error'));
(async()=>{
 await window.fetch('/api/events?after=2');assert.equal(fetches[0].options.headers.get('X-FT-Session'),'secret');assert.equal(fetches[0].options.credentials,'same-origin');
 await assert.rejects(window.fetch('https://example.com/'),/External/);assert.equal(fetches.length,1);
 assert.equal((await window.FTDesktop.request('/desktop/export-backup')).saved,true);
 console.log('Desktop adapter checks passed: durable acknowledgements, deduplication, failed-save cache preservation, revisions, deletion, authenticated fetch and external-origin rejection.');
})().catch(e=>{console.error(e);process.exitCode=1});
