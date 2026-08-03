(() => {
  'use strict';

  const SETTINGS_KEY = 'melvexOutreachDrafts';
  const leads = typeof rawLeads !== 'undefined' ? rawLeads : [];
  if (!leads.length || typeof crm === 'undefined') return;

  crm.settings ||= {};
  crm.settings[SETTINGS_KEY] ||= {};
  let selectedId = leadId(leads[0]);

  const pad = (value) => String(value).padStart(2, '0');
  const localDate = (date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
  const addDays = (amount) => {
    const date = new Date();
    date.setDate(date.getDate() + amount);
    return localDate(date);
  };
  const defaultDraft = (lead) => ({
    contactName: '',
    companyName: lead.nome || '',
    date1: addDays(2),
    time1: '10:00',
    date2: addDays(3),
    time2: '09:30'
  });
  const draftFor = (lead) => {
    const id = leadId(lead);
    return crm.settings[SETTINGS_KEY][id] ||= defaultDraft(lead);
  };
  const selectedLead = () => leads.find((lead) => leadId(lead) === selectedId) || leads[0];
  const formatDate = (value) => {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return '—';
    const [year, month, day] = value.split('-');
    return `${day}/${month}`;
  };
  const formatTime = (value) => {
    const [hour, minute] = String(value || '').split(':');
    if (!hour || minute === undefined) return '—';
    return minute === '00' ? `${Number(hour)}h` : `${Number(hour)}h${minute}`;
  };
  const phoneFor = (lead) => {
    let phone = String(lead.celular || '').replace(/\D/g, '');
    if (phone.length === 10 || phone.length === 11) phone = `55${phone}`;
    return /^\d{12,13}$/.test(phone) ? phone : '';
  };
  const validate = (draft) => {
    const first = new Date(`${draft.date1}T${draft.time1 || '00:00'}:00`);
    const second = new Date(`${draft.date2}T${draft.time2 || '00:00'}:00`);
    if (!draft.companyName.trim()) return 'Informe o nome da empresa.';
    if (!draft.date1 || !draft.time1 || !draft.date2 || !draft.time2) return 'Preencha as duas opções de data e horário.';
    if (Number.isNaN(first.getTime()) || Number.isNaN(second.getTime())) return 'Confira as datas e os horários.';
    if (first <= new Date()) return 'A primeira opção precisa estar no futuro.';
    if (second <= first) return 'A segunda opção precisa ser posterior à primeira.';
    return '';
  };
  const messageFor = (lead, draft) => {
    const greeting = draft.contactName.trim() ? `Olá, ${draft.contactName.trim()}, tudo bem?` : 'Olá, tudo bem?';
    return `${greeting}\n\nAnalisei com bastante atenção a presença digital da ${draft.companyName.trim()} e encontrei alguns pontos que hoje podem estar limitando a percepção de autoridade, a descoberta dos serviços e a geração de contatos pelo site.\n\nTambém identifiquei oportunidades interessantes para transformar o site em uma presença digital mais estratégica e compatível com a credibilidade do escritório.\n\nPreparei um diagnóstico visual para apresentar. A ideia é mostrar o que encontrei, ouvir as prioridades de vocês e definir o melhor caminho.\n\nPodemos conversar por aproximadamente 25 minutos? Tenho disponibilidade no dia ${formatDate(draft.date1)}, às ${formatTime(draft.time1)}, ou no dia ${formatDate(draft.date2)}, às ${formatTime(draft.time2)}. Algum desses horários funciona para você?`;
  };

  const studio = document.createElement('section');
  studio.className = 'outreach-studio';
  studio.id = 'outreach-studio';
  studio.setAttribute('aria-labelledby', 'outreach-title');
  studio.innerHTML = `
    <div class="outreach-editor">
      <div class="outreach-heading"><div><p class="outreach-kicker">Melvex outreach studio</p><h2 class="outreach-title" id="outreach-title">Personalize antes de abordar</h2></div><span class="badge" id="outreach-lead-tier"></span></div>
      <div class="outreach-grid">
        <label class="outreach-field"><span class="outreach-label">Nome do contato</span><input class="input" id="outreach-contact" autocomplete="off" placeholder="Nome da pessoa"></label>
        <label class="outreach-field"><span class="outreach-label">Empresa</span><input class="input" id="outreach-company" autocomplete="organization"></label>
        <fieldset class="slot-panel"><legend>Opção 1</legend><div class="slot-grid"><label class="outreach-field"><span class="outreach-label">Dia</span><input class="input" id="outreach-date-1" type="date"></label><label class="outreach-field"><span class="outreach-label">Hora</span><input class="input" id="outreach-time-1" type="time"></label></div></fieldset>
        <fieldset class="slot-panel"><legend>Opção 2</legend><div class="slot-grid"><label class="outreach-field"><span class="outreach-label">Dia</span><input class="input" id="outreach-date-2" type="date"></label><label class="outreach-field"><span class="outreach-label">Hora</span><input class="input" id="outreach-time-2" type="time"></label></div></fieldset>
      </div>
      <p class="outreach-error" id="outreach-error" role="alert"></p>
    </div>
    <div class="outreach-preview">
      <div class="outreach-heading"><div><p class="outreach-kicker">Prévia em tempo real</p><h2 class="outreach-title" id="outreach-company-title"></h2></div></div>
      <div class="message-bubble" id="outreach-message" aria-live="polite"></div>
      <div class="outreach-actions"><button class="btn" id="outreach-copy" type="button">Copiar mensagem</button><a class="btn" id="outreach-whatsapp" target="_blank" rel="noopener noreferrer">Abrir WhatsApp</a></div>
    </div>`;
  document.querySelector('.hero')?.after(studio);

  const fieldMap = {
    contactName: '#outreach-contact', companyName: '#outreach-company',
    date1: '#outreach-date-1', time1: '#outreach-time-1', date2: '#outreach-date-2', time2: '#outreach-time-2'
  };
  const nodes = Object.fromEntries(Object.entries(fieldMap).map(([key, selector]) => [key, document.querySelector(selector)]));

  function syncStudio() {
    const lead = selectedLead();
    const draft = draftFor(lead);
    Object.entries(nodes).forEach(([key, node]) => { if (node.value !== draft[key]) node.value = draft[key]; });
    const error = validate(draft);
    const phone = phoneFor(lead);
    const message = messageFor(lead, draft);
    document.querySelector('#outreach-company-title').textContent = draft.companyName || lead.nome;
    document.querySelector('#outreach-lead-tier').textContent = lead.tier || 'LEAD';
    document.querySelector('#outreach-message').textContent = message;
    document.querySelector('#outreach-error').textContent = error || (!phone ? 'Este lead não possui um WhatsApp válido.' : '');
    const whatsapp = document.querySelector('#outreach-whatsapp');
    whatsapp.href = !error && phone ? `https://wa.me/${phone}?text=${encodeURIComponent(message)}` : '#';
    whatsapp.setAttribute('aria-disabled', String(Boolean(error || !phone)));
    whatsapp.style.pointerEvents = error || !phone ? 'none' : '';
    document.querySelectorAll('.card').forEach((card) => card.classList.toggle('outreach-selected', card.dataset.id === selectedId));
  }

  Object.entries(nodes).forEach(([key, node]) => node.addEventListener('input', () => {
    draftFor(selectedLead())[key] = node.value;
    save();
    syncStudio();
  }));

  const originalRender = render;
  render = function melvexRender(...args) {
    originalRender(...args);
    document.querySelectorAll('.card').forEach((card) => {
      if (card.querySelector('[data-action="personalize"]')) return;
      const button = document.createElement('button');
      button.className = 'btn';
      button.type = 'button';
      button.dataset.action = 'personalize';
      button.textContent = card.dataset.id === selectedId ? 'Editando abordagem' : 'Personalizar abordagem';
      card.querySelector('.script')?.replaceWith(button);
    });
    syncStudio();
  };

  document.querySelector('#leads').addEventListener('click', (event) => {
    const button = event.target.closest('[data-action="personalize"]');
    if (!button) return;
    selectedId = button.closest('.card').dataset.id;
    render();
    studio.scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.querySelector('#outreach-contact').focus({ preventScroll: true });
  });

  document.querySelector('#outreach-copy').addEventListener('click', async () => {
    const draft = draftFor(selectedLead());
    const error = validate(draft);
    if (error) return syncStudio();
    const message = messageFor(selectedLead(), draft);
    try {
      await navigator.clipboard.writeText(message);
    } catch {
      const area = document.createElement('textarea');
      area.value = message; area.style.position = 'fixed'; area.style.opacity = '0';
      document.body.append(area); area.select(); document.execCommand('copy'); area.remove();
    }
    showToast('Mensagem personalizada copiada.');
  });

  document.querySelector('#outreach-whatsapp').addEventListener('click', () => {
    const lead = selectedLead();
    if (!validate(draftFor(lead)) && phoneFor(lead)) {
      addHistory(leadId(lead), 'Abordagem personalizada preparada para WhatsApp');
      save();
    }
  });

  render();
})();
