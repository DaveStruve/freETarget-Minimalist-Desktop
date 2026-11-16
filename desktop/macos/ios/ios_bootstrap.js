(()=>{
'use strict';
const boot=/*__FT_IOS_BOOT__*/;
const cache=new Map(Object.entries(boot.storage));let revision=boot.revision;
function fail(message){const error=Error(message);window.dispatchEvent(new CustomEvent('ft-storage-error',{detail:error.message}));return error}
function change(key,value,remove=false){
 let result;try{const raw=window.prompt('FT_STORE_V1',JSON.stringify({key,value,remove,expected_revision:revision}));if(!raw)throw Error('The native data service did not reply.');result=JSON.parse(raw)}catch(error){throw fail(error.message)}
 if(result.error)throw fail(result.error);if(!Number.isInteger(result.revision))throw fail('Invalid save acknowledgement.');
 revision=result.revision;if(remove)cache.delete(key);else cache.set(key,value);
}
function read(key){
 key=String(key);
 if(key==='ft-connection-method')return 'tcp';
 if(key==='ft-show-demo')return 'false';
 const value=cache.get(key)??null;
 if(key==='ft-last-successful-connection'&&value){
  try{if(JSON.parse(value)?.method!=='tcp')return null}catch{return null}
 }
 return value;
}
window.FTDesktopStorage=Object.freeze({getItem:read,setItem(key,value){key=String(key);value=String(value);if(cache.has(key)&&cache.get(key)===value)return;change(key,value)},removeItem(key){key=String(key);if(cache.has(key))change(key,null,true)},key:index=>Array.from(cache.keys())[index]??null,get length(){return cache.size}});
window.fetch=async(input,options={})=>{
 const path=typeof input==='string'?input:input.url;
 if(typeof path!=='string'||!path.startsWith('/')||path.startsWith('//'))throw Error('Only the bundled app can use the native target service.');
 const body=options.body?JSON.parse(options.body):{};
 const response=await window.webkit.messageHandlers.ft.postMessage({path,method:options.method||'GET',body});
 if(!response||!Number.isInteger(response.status))throw Error('The native service returned an invalid response.');
 return {ok:response.status>=200&&response.status<300,status:response.status,json:async()=>response.body,text:async()=>JSON.stringify(response.body)};
};
window.FTDesktop={get revision(){return revision},async request(path,body={}){const response=await window.fetch(path,{method:'POST',body:JSON.stringify(body)});const data=await response.json();if(!response.ok)throw Error(data.error||'Native operation failed.');return data}};
document.addEventListener('DOMContentLoaded',()=>{
 const get=id=>document.getElementById(id);
 for(const id of ['desktopBrowserExport','desktopOpenFolder','openTargetSettings','openTerminal','diagCopy'])if(get(id))get(id).hidden=true;
 const method=get('connectionMethod');
 method?.querySelector('option[value="serial"]')?.remove();
 get('connectionMethodSerial')?.closest('fieldset')?.setAttribute('hidden','');
 get('settingsHost')?.setAttribute('autocapitalize','none');
 get('settingsHost')?.setAttribute('autocorrect','off');
 get('settingsPort')?.setAttribute('inputmode','numeric');
 get('settingsBackup')?.querySelector('h3')?.replaceChildren('Data & Backups');
 const demo=get('showDemo')?.closest('label');
 demo?.setAttribute('hidden','');
 demo?.nextElementSibling?.setAttribute('hidden','');
 for(const id of ['resetDemoData','demoModeStatus'])get(id)?.setAttribute('hidden','');
 const folder=get('desktopDataFolder');if(folder)folder.textContent='On this device. Use Export Backup to save a copy in Files.';
 const help=document.querySelector('.desktopDataControls .settingsHelp');if(help)help.textContent='Designed for the freETarget Minimalist build. Profiles, guns, History and preferences are saved on this device. Export/import JSON backups through Files; export old browser data on your Mac or Windows PC first.';
 for(const p of document.querySelectorAll('.desktopDataControls .settingsHelp'))if(p.textContent.includes('To migrate:'))p.textContent='To migrate, create a JSON export on the Mac or Windows app first, transfer it through Files, then choose Restore / Migrate Data. Log the current result before exporting. Deleting the iOS app removes its local records; export a backup first.';
});
})();
