// === Dynamic branching questions ===
// Example schema you can extend freely:
const QUESTION_TREE = {
  q1: {
    label: "Workcube Kullanım Durumunuz?",
    type: "single",
    options: [
      { value: "no", text: "Hayır, Kullanılmıyor", children: ["q2"] },
      { value: "partial", text: "Kısmen Kullanılıyor", children: ["q2","q3"] },
      { value: "full", text: "Tam Entegre Kullanım", children: ["q3","q4"] },
    ]
  },
  q2: {
    label: "Hangi Modüllere İhtiyaç Var? (Çoklu Seçim)",
    type: "multi",
    options: [
      { value: "finance", text: "Finans & Muhasebe" },
      { value: "inventory", text: "Stok & Depo" },
      { value: "production", text: "Üretim/MRP" },
      { value: "quality", text: "Kalite & İzlenebilirlik" },
      { value: "crm", text: "CRM & Satış" },
      { value: "hr", text: "İK" },
      { value: "bpm", text: "Süreç/BPM" },
    ],
    children: {
      // if includes "production", then ask q2a
      includeAny: { keys: ["production"], next: ["q2a"] }
    }
  },
  q2a: {
    label: "Üretim Planlama İhtiyacı",
    type: "single",
    options: [
      { value: "basic", text: "Temel Planlama" },
      { value: "mrp", text: "MRP / Gelişmiş Planlama" }
    ]
  },
  q3: {
    label: "Entegrasyon İhtiyacı Var mı?",
    type: "single",
    options: [
      { value: "none", text: "Hayır" },
      { value: "iot", text: "IoT/Makine Entegrasyonu" },
      { value: "ecomm", text: "E-Ticaret/Marketplace" },
      { value: "logistics", text: "Lojistik/3PL" },
    ]
  },
  q4: {
    label: "Karar Verme Süreciniz",
    type: "single",
    options: [
      { value: "1m", text: "1 Ay" },
      { value: "3m", text: "3 Ay" },
      { value: "6m", text: "6 Ay+" },
    ]
  }
};

function renderQuestion(key, container, answers){
  const node = QUESTION_TREE[key];
  if(!node) return;
  const wrap = document.createElement('div');
  wrap.className = 'card';
  wrap.style.margin='12px 0';
  const id = `q_${key}`;
  let html = `<div><label style="font-weight:700">${node.label}</label></div>`;
  if(node.type === 'single'){
    html += node.options.map((opt, idx)=>{
      const name = id;
      const checked = answers[key]===opt.value ? 'checked' : '';
      return `<label style="display:block; margin:6px 0;">
        <input type="radio" name="${name}" value="${opt.value}" ${checked}/> ${opt.text}
      </label>`;
    }).join('');
  } else if(node.type === 'multi'){
    const prev = Array.isArray(answers[key]) ? answers[key] : [];
    html += node.options.map(opt=>{
      const checked = prev.includes(opt.value) ? 'checked' : '';
      return `<label style="display:block; margin:6px 0;">
        <input type="checkbox" name="${id}" value="${opt.value}" ${checked}/> ${opt.text}
      </label>`;
    }).join('');
  }
  wrap.innerHTML = html;
  container.appendChild(wrap);

  // children by option selection (single)
  if(node.type==='single'){
    node.options.forEach(opt=>{
      if(opt.children && answers[key]===opt.value){
        opt.children.forEach(child=> renderQuestion(child, container, answers));
      }
    });
  }

  // children by includeAny (multi)
  if(node.type==='multi' && node.children && node.children.includeAny){
    const prev = Array.isArray(answers[key]) ? answers[key] : [];
    const cond = node.children.includeAny;
    const hit = (cond.keys || []).some(k=> prev.includes(k));
    if(hit){
      (cond.next||[]).forEach(child=> renderQuestion(child, container, answers));
    }
  }
}

function computeProgress(){
  const inputs = document.querySelectorAll('#questions input');
  const totalGroups = new Set();
  inputs.forEach(i=> totalGroups.add(i.getAttribute('name')));
  let answered = 0;
  totalGroups.forEach(name=>{
    const group = document.querySelectorAll(`input[name="${name}"]`);
    const anyChecked = Array.from(group).some(i=> (i.type==='radio' && i.checked) || (i.type==='checkbox' && i.checked));
    if(anyChecked) answered++;
  });
  const pct = totalGroups.size===0 ? 0 : Math.round(answered*100/totalGroups.size);
  document.getElementById('bar').style.width = pct + '%';
}

function readAnswers(){
  const result = {};
  // radios
  document.querySelectorAll('#questions input[type="radio"]').forEach(i=>{
    const key = i.getAttribute('name').replace('q_','');
    if(i.checked){ result[key] = i.value; }
  });
  // checkboxes
  const groups = {};
  document.querySelectorAll('#questions input[type="checkbox"]').forEach(i=>{
    const name = i.getAttribute('name');
    groups[name] = groups[name] || [];
    if(i.checked) groups[name].push(i.value);
  });
  Object.entries(groups).forEach(([k,v])=>{
    const key = k.replace('q_','');
    result[key] = v;
  });
  return result;
}

function initAssessment(){
  const container = document.getElementById('questions');
  container.innerHTML='';
  const answers = {}; // could be restored from localStorage if needed
  renderQuestion('q1', container, answers);
  container.addEventListener('change', e=>{
    // re-render on any change to satisfy infinite branching
    const ans = readAnswers();
    container.innerHTML='';
    renderQuestion('q1', container, ans);
    computeProgress();
  });
  computeProgress();
}

function validatePhone(phone){
  return /^[0-9+\-()\s]{7,20}$/.test(phone);
}

async function submitForm(ev){
  ev.preventDefault();
  const fd = new FormData(document.getElementById('form'));
  const payload = {
    tax_id: (fd.get('tax_id')||'').trim(),
    full_name: (fd.get('full_name')||'').trim(),
    email: (fd.get('email')||'').trim(),
    company: (fd.get('company')||'').trim(),
    phone: (fd.get('phone')||'').trim(),
    answers: readAnswers(),
    meta: {
      userAgent: navigator.userAgent
    }
  };
  // simple validations
  if(payload.tax_id && !/^\d{10,11}$/.test(payload.tax_id)){ alert('TC/Vergi No 10-11 hane olmalı'); return false; }
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)){ alert('E-posta formatı hatalı'); return false; }
  if(!validatePhone(payload.phone)){ alert('Telefon formatı hatalı'); return false; }

  const res = await fetch('/api/assessments', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if(!res.ok || !data.ok){
    alert('Kayıt sırasında bir hata oluştu');
    return false;
  }
  alert('Teşekkürler! Kaydınız alındı.' + (data.email_error ? ('\nE-posta gönderim hatası: '+data.email_error) : ''));
  document.getElementById('form').reset();
  initAssessment();
  return false;
}
