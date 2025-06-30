window.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('monster-detail-modal');
  const modalBody = document.getElementById('modal-card-body');

  let equipmentList = [];
  let equipUrl = '';
  const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
  const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';
  const dataElem = document.getElementById('party-data');
  if (dataElem) {
    try {
      const parsed = JSON.parse(dataElem.textContent);
      equipmentList = parsed.equipment_list || [];
      equipUrl = parsed.equip_url || '';
    } catch (e) {
      console.error('Failed to parse party-data', e);
    }
  }

  // Helper to update text content of an element
  function updateTextContent(elementId, text) {
    const el = document.getElementById(elementId);
    if (el) el.textContent = text;
  }

  // Helper to update monster stats in the modal
  function updateMonsterStatsInModal(data) {
    updateTextContent('detail-level', data.level);
    updateTextContent('detail-hp', data.hp);
    updateTextContent('detail-max-hp', data.max_hp);
    updateTextContent('detail-mp', data.mp);
    updateTextContent('detail-max-mp', data.max_mp);
    updateTextContent('detail-attack', data.stats.attack);
    updateTextContent('detail-defense', data.stats.defense);
    updateTextContent('detail-speed', data.stats.speed);
    
    const statusesText = (data.statuses || []).map(s => `${s.display}(${s.remaining})`).join('、');
    updateTextContent('detail-statuses', statusesText);
  }

  // Helper to rebuild the equipped items list
  function rebuildEquippedList(data) {
    const equippedUl = modalBody.querySelector('.card-equipment-list ul');
    if (!equippedUl) return;
    equippedUl.textContent = ''; // Clear existing list

    (data.equipment_slots || []).forEach(slot => {
      const li = document.createElement('li');
      const name = data.equipment && data.equipment[slot] ? data.equipment[slot] : '空き';
      li.textContent = slot + ': ' + name;
      if (data.equipment && data.equipment[slot]) {
        const btn = document.createElement('button');
        btn.className = 'unequip-btn';
        btn.dataset.slot = slot;
        btn.dataset.idx = data.index;
        btn.textContent = '外す';
        li.appendChild(document.createTextNode(' '));
        li.appendChild(btn);
      }
      equippedUl.appendChild(li);
    });
    attachUnequipListeners(); // Re-attach listeners
  }

  // Helper to rebuild the inventory list
  function rebuildInventoryList(data) {
    const equipSection = modalBody.querySelector('.card-equipment-list');
    if (!equipSection) return;

    let invUl = equipSection.querySelector('.inventory-list');
    if (!invUl) {
      invUl = document.createElement('ul');
      invUl.className = 'inventory-list';
      const equipHeader2 = document.createElement('h3');
      equipHeader2.textContent = '装備する';
      equipSection.appendChild(equipHeader2);
      equipSection.appendChild(invUl);
    }
    invUl.textContent = ''; // Clear existing list

    if (equipmentList.length > 0) {
      equipmentList.forEach(eq => {
        const li = document.createElement('li');
        const btn = document.createElement('button');
        btn.className = 'equip-btn';
        btn.dataset.equipId = eq.id;
        btn.dataset.idx = data.index; // data.index needs to be accessible
        btn.textContent = '装備';
        li.textContent = eq.name + ' ';
        li.appendChild(btn);
        invUl.appendChild(li);
      });
      attachEquipListeners(); // Re-attach listeners
    } else {
      const p = document.createElement('p');
      p.textContent = '装備を持っていない。';
      invUl.appendChild(p); // Append to invUl, not equipSection directly
    }
  }

  function displayMonsterDetails(data) {
    // Store current data for partial updates
    modal.currentMonsterData = data;

    modalBody.textContent = ''; // Clear previous content

    const expNeeded = data.exp_to_next - data.exp;

    // Image Area
    const imgArea = document.createElement('div');
    imgArea.className = 'card-image-area';
    const img = document.createElement('img');
    img.src = data.image;
    img.alt = data.name;
    img.className = 'card-monster-img';
    imgArea.appendChild(img);
    modalBody.appendChild(imgArea);

    // Header
    const header = document.createElement('div');
    header.className = 'card-header';
    const h2 = document.createElement('h2');
    h2.id = 'modal-title';
    h2.className = 'card-monster-name';
    h2.textContent = data.name;
    header.appendChild(h2);
    const lvhp = document.createElement('div');
    lvhp.className = 'card-monster-lvhp';
    const spanLv = document.createElement('span');
    spanLv.id = 'detail-level';
    spanLv.textContent = 'Lv. ' + data.level;
    const spanHp = document.createElement('span');
    spanHp.id = 'detail-hp';
    spanHp.textContent = 'HP: ' + data.hp;
    const spanMaxHp = document.createElement('span');
    spanMaxHp.id = 'detail-max-hp';
    spanMaxHp.textContent = ' / ' + data.max_hp;
    const spanMp = document.createElement('span');
    spanMp.id = 'detail-mp';
    spanMp.textContent = 'MP: ' + data.mp;
    const spanMaxMp = document.createElement('span');
    spanMaxMp.id = 'detail-max-mp';
    spanMaxMp.textContent = ' / ' + data.max_mp;
    const spanExp = document.createElement('span');
    spanExp.id = 'detail-exp';
    spanExp.textContent = 'EXP: ' + data.exp + ' / ' + data.exp_to_next + ' (残り ' + expNeeded + ')';
    lvhp.append(spanLv, document.createTextNode(' | '), spanHp, spanMaxHp, document.createTextNode(' | '), spanMp, spanMaxMp, document.createTextNode(' | '), spanExp);
    header.appendChild(lvhp);
    modalBody.appendChild(header);

    // Content Area
    const content = document.createElement('div');
    content.className = 'card-content';

    // Stats Grid
    const statsGrid = document.createElement('div');
    statsGrid.className = 'card-stats-grid';
    const atkSpan = document.createElement('span');
    atkSpan.textContent = 'こうげき: ';
    const atkVal = document.createElement('strong');
    atkVal.id = 'detail-attack';
    atkVal.textContent = data.stats.attack;
    atkSpan.appendChild(atkVal);
    statsGrid.appendChild(atkSpan);
    const defSpan = document.createElement('span');
    defSpan.textContent = 'ぼうぎょ: ';
    const defVal = document.createElement('strong');
    defVal.id = 'detail-defense';
    defVal.textContent = data.stats.defense;
    defSpan.appendChild(defVal);
    statsGrid.appendChild(defSpan);
    const spdSpan = document.createElement('span');
    spdSpan.textContent = 'すばやさ: ';
    const spdVal = document.createElement('strong');
    spdVal.id = 'detail-speed';
    spdVal.textContent = data.stats.speed;
    spdSpan.appendChild(spdVal);
    statsGrid.appendChild(spdSpan);
    content.appendChild(statsGrid);

    // Skills Section
    const skillsSection = document.createElement('div');
    skillsSection.className = 'card-section card-skills-list';
    const skillsHeader = document.createElement('h3');
    skillsHeader.textContent = 'スキル';
    skillsSection.appendChild(skillsHeader);
    if (data.skills && data.skills.length > 0) {
      const ul = document.createElement('ul');
      data.skills.forEach(skill => {
        const li = document.createElement('li');
        const strong = document.createElement('strong');
        strong.textContent = skill.name;
        li.appendChild(strong);
        li.appendChild(document.createTextNode(': ' + skill.description));
        ul.appendChild(li);
      });
      skillsSection.appendChild(ul);
    } else {
      const p = document.createElement('p');
      p.textContent = '覚えているスキルはない。';
      skillsSection.appendChild(p);
    }
    content.appendChild(skillsSection);

    // Description Section
    const descSection = document.createElement('div');
    descSection.className = 'card-section card-description';
    descSection.style.marginTop = '16px';
    const descHeader = document.createElement('h3');
    descHeader.textContent = '説明';
    const descP = document.createElement('p');
    descP.textContent = data.description;
    descSection.append(descHeader, descP);
    content.appendChild(descSection);

    // Equipment Section
    if (data.index !== undefined && data.index >= 0) {
      const equipSection = document.createElement('div');
      equipSection.className = 'card-section card-equipment-list';
      equipSection.style.marginTop = '16px';
      const equipHeader = document.createElement('h3');
      equipHeader.textContent = '装備中';
      equipSection.appendChild(equipHeader);

      const equippedUl = document.createElement('ul');
      equippedUl.id = 'equipped-list'; // Add ID for easier access
      equipSection.appendChild(equippedUl);
      
      const equipHeader2 = document.createElement('h3');
      equipHeader2.textContent = '装備する';
      equipSection.appendChild(equipHeader2);

      const invUl = document.createElement('ul');
      invUl.className = 'inventory-list'; // Add class for easier access
      equipSection.appendChild(invUl);

      content.appendChild(equipSection);
    }
    modalBody.appendChild(content);

    // Initial population of equipped and inventory lists
    rebuildEquippedList(data);
    rebuildInventoryList(data); // Pass data to rebuildInventoryList

    modal.classList.add('show');
    modal.focus();
  }

  // Attach listeners for equip/unequip buttons
  function attachEquipListeners() {
    modalBody.querySelectorAll('.equip-btn').forEach(btn => {
      btn.onclick = null; // Remove old listeners
      btn.addEventListener('click', () => {
        btn.disabled = true;
        const equipId = btn.dataset.equipId;
        const idx = modal.currentMonsterData.index; // Use stored data
        fetch(equipUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
          body: JSON.stringify({ equip_id: equipId, monster_idx: idx })
        })
        .then(res => res.json())
        .then(resp => {
          if (resp.success) {
            equipmentList.length = 0;
            resp.equipment_inventory.forEach(e => equipmentList.push(e));
            modal.currentMonsterData.equipment = resp.monster_equipment;
            if (resp.monster_stats) modal.currentMonsterData.stats = resp.monster_stats;
            
            // Partial UI updates
            updateMonsterStatsInModal(modal.currentMonsterData);
            rebuildEquippedList(modal.currentMonsterData);
            rebuildInventoryList(modal.currentMonsterData);
          } else {
            alert('装備の更新に失敗しました: ' + (resp.message || '不明なエラー'));
          }
        })
        .catch(err => {
          console.error('Fetch error', err);
          alert('通信エラー: ' + err.message);
        })
        .finally(() => { btn.disabled = false; });
      });
    });
  }

  function attachUnequipListeners() {
    modalBody.querySelectorAll('.unequip-btn').forEach(btn => {
      btn.onclick = null; // Remove old listeners
      btn.addEventListener('click', () => {
        btn.disabled = true;
        const idx = modal.currentMonsterData.index; // Use stored data
        const slot = btn.dataset.slot;
        fetch(equipUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
          body: JSON.stringify({ equip_id: null, monster_idx: idx, slot: slot })
        })
        .then(res => res.json())
        .then(resp => {
          if (resp.success) {
            equipmentList.length = 0;
            resp.equipment_inventory.forEach(e => equipmentList.push(e));
            modal.currentMonsterData.equipment = resp.monster_equipment;
            if (resp.monster_stats) modal.currentMonsterData.stats = resp.monster_stats;

            // Partial UI updates
            updateMonsterStatsInModal(modal.currentMonsterData);
            rebuildEquippedList(modal.currentMonsterData);
            rebuildInventoryList(modal.currentMonsterData);
          } else {
            alert('装備の更新に失敗しました: ' + (resp.message || '不明なエラー'));
          }
        })
        .catch(err => {
          console.error('Fetch error', err);
          alert('通信エラー: ' + err.message);
        })
        .finally(() => { btn.disabled = false; });
      });
    });
  }

  function closeModal() { modal.classList.remove('show'); }
  modal.querySelector('.modal-close-btn').addEventListener('click', closeModal);
  modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
  modal.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

  document.querySelectorAll('.monster-item').forEach(item => {
    item.addEventListener('click', () => {
      const data = JSON.parse(item.dataset.details);
      displayMonsterDetails(data);
    });
  });

  // drag and drop
  const dropAreas = document.querySelectorAll('.drop-area');
  let draggedItem = null;

  document.querySelectorAll('.monster-item').forEach(draggable => {
    draggable.addEventListener('dragstart', e => {
      draggedItem = e.target;
      setTimeout(() => draggedItem.classList.add('dragging'), 0);
    });
    draggable.addEventListener('dragend', () => {
      if (draggedItem) draggedItem.classList.remove('dragging');
      draggedItem = null;
    });
  });

  dropAreas.forEach(area => {
    area.addEventListener('dragover', e => { e.preventDefault(); area.classList.add('drag-over'); });
    area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
    area.addEventListener('drop', e => {
      e.preventDefault();
      area.classList.remove('drag-over');
      if (!draggedItem) return;
      const existing = area.querySelector('.monster-item');
      if (existing && existing !== draggedItem) {
        // Swap logic: move existing item to where draggedItem came from
        const originalParent = draggedItem.parentElement;
        originalParent.appendChild(existing);
      }
      area.appendChild(draggedItem);
    });
  });

  const confirmBtn = document.getElementById('confirm-btn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', e => {
      e.preventDefault();
      const order = [];
      document.querySelectorAll('.team-slots .monster-item').forEach(el => order.push(el.dataset.uid));
      const reserve = [];
      document.querySelectorAll('#monster-pool .monster-item').forEach(el => reserve.push(el.dataset.uid));
      document.getElementById('order-input').value = JSON.stringify(order);
      document.getElementById('reserve-input').value = JSON.stringify(reserve);
      document.getElementById('formation-form').submit();
    });
  }
});
