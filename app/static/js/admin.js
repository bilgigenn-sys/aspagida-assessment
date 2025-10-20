function token(){ return localStorage.getItem('token') || ''; }

async function needAuth(res){
  if(res.status===401){ location.href='/login'; return true; }
  return false;
}

async function loadStats(){
  const res = await fetch('/api/stats', { headers: { 'Authorization':'Bearer '+token() }});
  if(await needAuth(res)) return;
  const d = await res.json();
  document.getElementById('total').innerText = d.total_tests;
  document.getElementById('today').innerText = d.todays_tests;
  document.getElementById('companies').innerText = d.companies;
}

async function loadList(){
  const res = await fetch('/api/assessments', { headers: { 'Authorization':'Bearer '+token() }});
  if(await needAuth(res)) return;
  const rows = await res.json();
  const tbody = document.querySelector('#tbl tbody');
  tbody.innerHTML='';
  rows.forEach(r=>{
    const tr = document.createElement('tr');
    const pdfLink = r.id ? `<a href="/api/assessments/${r.id}/pdf" target="_blank">PDF</a>` : '-';
    tr.innerHTML = `<td>${r.id}</td><td>${r.created_at}</td><td>${r.full_name}</td><td>${r.company||''}</td><td>${r.email}</td><td>${r.phone}</td><td>${pdfLink}</td>`;
    tbody.appendChild(tr);
  });
}

async function loadSMTP(){
  const res = await fetch('/api/smtp', { headers: { 'Authorization':'Bearer '+token() }});
  if(await needAuth(res)) return;
  const d = await res.json();
  document.getElementById('smtp_host').value = d.host;
  document.getElementById('smtp_port').value = d.port;
  document.getElementById('smtp_user').value = d.username || '';
  document.getElementById('smtp_tls').value = d.use_tls ? 'true' : 'false';
}

async function saveSMTP(){
  const payload = {
    host: document.getElementById('smtp_host').value.trim(),
    port: parseInt(document.getElementById('smtp_port').value,10),
    username: document.getElementById('smtp_user').value.trim() || null,
    password: document.getElementById('smtp_pass').value || null,
    use_tls: document.getElementById('smtp_tls').value==='true'
  };
  const res = await fetch('/api/smtp',{
    method:'PUT',
    headers:{'Content-Type':'application/json','Authorization':'Bearer '+token()},
    body: JSON.stringify(payload)
  });
  if(await needAuth(res)) return;
  if(!res.ok){ alert('Kaydedilemedi'); return; }
  alert('SMTP ayarları güncellendi');
}

window.addEventListener('DOMContentLoaded', async ()=>{
  await loadStats();
  await loadList();
  await loadSMTP();
});
