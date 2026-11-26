(() => {
  'use strict';

  let lastTimestamp = 0;
  let currentImuShot = null;
  const defaults = {enabled:true,width:5,duration:1000,demo:true};
  const storage = window.FTDesktopStorage || localStorage;
  const key = 'ft-imu-settings-v1';
  let settings = {...defaults};
  try { Object.assign(settings, JSON.parse(storage.getItem(key)||'{}')); } catch(e) {}
  settings.width = Math.max(1,Math.min(10,Number(settings.width)||5));
  settings.duration = Math.max(100,Math.min(1000,Number(settings.duration)||1000));
  const el = id => document.getElementById(id);
  let busy = false, polling = false;
  function sync() {
    el('imuEnabled').checked=settings.enabled;
    el('imuWidth').value=settings.width; el('imuWidthValue').textContent=settings.width+' px';
    el('imuDuration').value=settings.duration; el('imuDurationValue').textContent=settings.duration+' ms';
    el('imuDemo').checked=settings.demo;
    for(const id of ['imuWidth','imuDuration','imuDemo']) el(id).disabled=!settings.enabled;
    ensureImuBadge().style.display=settings.enabled?'flex':'none';
    window.ftRefreshImuTarget?.();
  }
  function save() { try {storage.setItem(key,JSON.stringify(settings));} catch(e){el('imuStatus').textContent='Réglages non enregistrés : '+e.message;} }
  async function toggle(next) {
    if(busy)return;
    busy=true; el('imuEnabled').disabled=true; el('imuReset').disabled=true;
    settings.enabled=next; currentImuShot=null; sync();
    try { await window.FTDesktop.request('/desktop/imu/settings',{enabled:next}); save(); }
    catch(e){ settings.enabled=!next; el('imuStatus').textContent=e.message; sync(); }
    finally {busy=false;el('imuEnabled').disabled=false;el('imuReset').disabled=false;}
  }


  // 1. Crée le bandeau de télémétrie en bas à droite
  function ensureImuBadge() {
    let badge = document.getElementById('ft-imu-telemetry');
    if (badge) return badge;

    badge = document.createElement('div');
    badge.id = 'ft-imu-telemetry';
    badge.style.cssText = [
      'position: fixed',
      'bottom: 50px',
      'right: 14px',
      'z-index: 9999',
      'padding: 10px 14px',
      'border-radius: 8px',
      'background: rgba(15, 23, 42, 0.94)',
      'color: #f8fafc',
      'font-size: 12px',
      'font-family: monospace',
      'border-left: 4px solid #64748b',
      'box-shadow: 0 4px 12px rgba(0,0,0,0.35)',
      'display: flex',
      'flex-direction: column',
      'gap: 4px',
      'pointer-events: none'
    ].join(';');
    badge.textContent = 'IMU P8X : Initialisation...';

    document.body.appendChild(badge);
    return badge;
  }

  // Trajectoire sur le SVG natif (repère 400x400), ancrée sur le dernier impact.
  window.ftDrawImuTrace = function(group, dims, displayedShots) {
    if (!settings.enabled || !currentImuShot?.points || currentImuShot.points.length < 2) return;
    const hit = displayedShots.length ? displayedShots[displayedShots.length - 1] : null;
    if (!hit || hit.miss) return;
    const scale = 340 / dims.rings[0];
    const cx = 200 + hit.x * scale, cy = 200 + hit.y * scale;
    const pts = currentImuShot.points;
    const cut1 = Math.floor(pts.length * .8), cut2 = Math.floor(pts.length * .9);
    const ns = 'http://www.w3.org/2000/svg';
    const segments = [
      [pts.slice(0,cut1+1),'#00aaff',2],
      [pts.slice(cut1,cut2+1),'#ffcc00',2],
      [pts.slice(cut2),currentImuShot.coup_de_doigt?'#ff3333':'#22c55e',2]
    ];
    const cutoff = pts[pts.length-1].t-settings.duration;
    for (const [raw,color] of segments) {
      const segment = raw.filter(p=>p.t>=cutoff);
      const first = raw.findIndex(p=>p.t>=cutoff);
      if(first>0 && raw[first].t>cutoff){const a=raw[first-1],b=raw[first],f=(cutoff-a.t)/(b.t-a.t);segment.unshift({x:a.x+(b.x-a.x)*f,y:a.y+(b.y-a.y)*f,t:cutoff});}
      if (segment.length < 2) continue;
      const path = document.createElementNS(ns,'path');
      path.setAttribute('d',segment.map((p,i)=>(i?'L':'M')+(cx+p.x*scale)+' '+(cy-p.y*scale)).join(' '));
      path.setAttribute('fill','none');path.setAttribute('stroke',color);
      path.setAttribute('vector-effect','non-scaling-stroke');
      path.setAttribute('stroke-width',settings.width);path.setAttribute('stroke-linecap','round');
      path.setAttribute('stroke-linejoin','round');
      group.appendChild(path);
    }
  };

  // 4. Interroge le serveur local Python /desktop/imu
  async function pollImu() {
    if(busy || polling)return;
    polling=true;
    const badge = ensureImuBadge();

    try {
      const res = await fetch('/desktop/imu');
      if (!res.ok) {
        badge.style.borderLeftColor = '#f59e0b';
        badge.textContent = `IMU P8X : Erreur HTTP ${res.status}`;
        return;
      }
      const data = await res.json();

      if(busy)return;
      el('imuStatus').textContent=!settings.enabled?'Désactivé':data.connected?'BLE connecté':'Recherche du capteur BLE…';
      if(!settings.enabled)return;
      if (!data.enabled || !data.connected) {
        badge.style.borderLeftColor = '#64748b';
        badge.textContent = 'IMU P8X : En attente du capteur BLE (P8X-BLE)...';
        return;
      }

      if (!data.latest_shot) {
        badge.style.borderLeftColor = '#0ea5e9';
        badge.textContent = 'IMU P8X : Connecté — Prêt pour le tir';
        return;
      }

      const shot = data.latest_shot;
      if (shot.timestamp !== lastTimestamp) {
        lastTimestamp = shot.timestamp;

        currentImuShot = shot;
        const created = settings.demo && typeof window.ftIngestImuDemoShot === 'function' && window.ftIngestImuDemoShot();
        // Rafraîchit le rendu SVG après l'enregistrement du tir.
        setTimeout(() => {
          if(!settings.enabled || currentImuShot!==shot)return;
          const flinch = shot.coup_de_doigt;

          badge.style.borderLeftColor = flinch ? '#ef4444' : '#22c55e';
          badge.innerHTML =
            `<div><strong>IMU P8X</strong> | L1: ${shot.l1_mm} mm | <strong>L0.2: ${shot.l02_mm} mm</strong></div>` +
            `<div style="color:${flinch ? '#f87171' : '#4ade80'};font-weight:bold;">` +
            `${flinch ? '⚠ COUP DE DOIGT (' + shot.pic_vitesse_mms + ' mm/s)' : '✓ LÂCHER PROPRE'}</div>`;

          if (typeof window.ftRefreshImuTarget === 'function') window.ftRefreshImuTarget();
        }, 50);
      }
    } catch (err) {
      badge.style.borderLeftColor = '#ef4444';
      badge.textContent = 'IMU P8X : Erreur (' + err.message + ')';
      el('imuStatus').textContent=err.message;
    } finally {polling=false;}
  }

  el('imuEnabled').onchange=e=>toggle(e.target.checked);
  for(const [id,k] of [['imuWidth','width'],['imuDuration','duration']]){
    el(id).oninput=e=>{settings[k]=Number(e.target.value);sync();};
    el(id).onchange=save;
  }
  el('imuDemo').onchange=e=>{settings.demo=e.target.checked;save();};
  el('imuReset').onclick=()=>{settings.width=5;settings.duration=1000;settings.demo=true;sync();save();if(!settings.enabled)toggle(true);};
  sync();
  pollImu();
  setInterval(pollImu, 300);
})();
