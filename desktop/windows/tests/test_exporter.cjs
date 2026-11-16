const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(path.join(__dirname,'../app/assets/browser_export.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
async function scenario({withLogo=false,missingDB=false,empty=false,blocked=false}={}){
 const storage=empty?{}:{'unrelated':'preserve','ft-shooter-profiles-v1':JSON.stringify([{name:'David',guns:[{model:'C55P'}]}]),'ft-session-history-v1':'[{"mode":"Five-Shot Standard"}]','ft-theme':'dark'};
 const original=JSON.stringify(storage),elements={summary:{},status:{},download:{disabled:true}},modes=[];let dataBlob,aborted=0,closed=0;
 const logo={name:'Club',width:600,height:200,dataURL:'data:image/png;base64,AAA='};
 const indexedDB={open(name){assert.equal(name,'ft-branding-v1');const request={transaction:{abort(){aborted++;setImmediate(()=>request.onerror())}}};setImmediate(()=>{
  if(blocked){request.onblocked();return}
  if(missingDB){request.onupgradeneeded();return}
  const db={objectStoreNames:{contains:name=>name==='logos'},close(){closed++},transaction(name,mode){modes.push(mode);const tx={objectStore(){return {get(key){assert.equal(key,'custom');const read={};setImmediate(()=>{read.result=withLogo?logo:undefined;read.onsuccess();tx.oncomplete()});return read}}}};return tx}};
  request.result=db;request.onsuccess();
 });return request}};
 const window={indexedDB},ctx={window,indexedDB,document:{getElementById:id=>elements[id],createElement:tag=>{assert.equal(tag,'a');return {click(){}}}},location:{origin:'http://127.0.0.1:8765'},localStorage:{get length(){return Object.keys(storage).length},key:i=>Object.keys(storage)[i],getItem:k=>storage[k],setItem(){throw Error('Exporter must not write localStorage')},removeItem(){throw Error('Exporter must not remove localStorage')}},setTimeout,clearTimeout,Date,Blob,URL:{createObjectURL(blob){dataBlob=blob;return 'blob:test'},revokeObjectURL(){}}};
 vm.createContext(ctx);vm.runInContext(script,ctx);for(let i=0;i<6;i++)await new Promise(r=>setImmediate(r));
 assert.equal(JSON.stringify(storage),original);assert.ok(modes.every(x=>x==='readonly'));
 if(blocked){assert.ok(elements.status.textContent.includes('blocked'));assert.equal(elements.download.disabled,true);return}
 if(empty){assert.equal(elements.download.disabled,true);return}
 assert.equal(elements.download.disabled,false);assert.ok(elements.summary.textContent.includes('1 Shooters'));assert.ok(elements.summary.textContent.includes('1 Guns'));assert.ok(elements.summary.textContent.includes('1 Saved Sessions'));
 elements.download.onclick();const output=JSON.parse(await dataBlob.text());assert.equal(output.format,'freetarget-browser-export');assert.equal(output.schema,1);assert.equal(output.storage.unrelated,undefined);assert.equal(output.storage['ft-theme'],'dark');assert.deepEqual(output.logo,withLogo?logo:null);
 if(missingDB)assert.equal(aborted,1);else assert.equal(closed,1);
}
(async()=>{await scenario({withLogo:true});await scenario({missingDB:true});await scenario({empty:true});await scenario({blocked:true});console.log('Browser migration checks passed: read-only storage/IndexedDB, logo export, absent database abort, empty-origin guidance and blocked database errors.');})().catch(e=>{console.error(e);process.exitCode=1});
