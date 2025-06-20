  window.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.fade-in').classList.add('show');
    const modal = document.getElementById('monster-detail-modal');
    const modalCardBody = document.getElementById('modal-card-body');
    const partyMembers = document.querySelectorAll('.party-member');

    let equipmentList = [];
    let equipUrl = '';
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

    let currentData = null;

    partyMembers.forEach(member => {
      member.addEventListener('click', () => {
        const monsterData = JSON.parse(member.dataset.details);
        currentData = monsterData;
        displayMonsterDetails(monsterData);
      });

      member.addEventListener('mouseenter', () => member.classList.add('magic-hover'));
      member.addEventListener('mouseleave', () => member.classList.remove('magic-hover'));
    });

    function displayMonsterDetails(data) {
      modalCardBody.textContent = '';

      const expNeeded = data.exp_to_next - data.exp;

      const imgArea = document.createElement('div');
      imgArea.className = 'card-image-area';
      const img = document.createElement('img');
      img.src = data.image;
      img.alt = data.name;
      img.className = 'card-monster-img';
      imgArea.appendChild(img);
      modalCardBody.appendChild(imgArea);

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
      spanLv.textContent = 'Lv. ' + data.level;
      const spanHp = document.createElement('span');
      spanHp.textContent = 'HP: ' + data.hp + ' / ' + data.max_hp;
      const spanExp = document.createElement('span');
      spanExp.textContent = 'EXP: ' + data.exp + ' / ' + data.exp_to_next + ' (残り ' + expNeeded + ')';
      lvhp.append(spanLv, document.createTextNode(' | '), spanHp, document.createTextNode(' | '), spanExp);
      header.appendChild(lvhp);
      modalCardBody.appendChild(header);

      const content = document.createElement('div');
      content.className = 'card-content';

      const statsGrid = document.createElement('div');
      statsGrid.className = 'card-stats-grid';

      const atkSpan = document.createElement('span');
      atkSpan.textContent = 'こうげき: ';
      const atkVal = document.createElement('strong');
      atkVal.textContent = data.stats.attack;
      atkSpan.appendChild(atkVal);
      statsGrid.appendChild(atkSpan);

      const defSpan = document.createElement('span');
      defSpan.textContent = 'ぼうぎょ: ';
      const defVal = document.createElement('strong');
      defVal.textContent = data.stats.defense;
      defSpan.appendChild(defVal);
      statsGrid.appendChild(defSpan);

      const spdSpan = document.createElement('span');
      spdSpan.textContent = 'すばやさ: ';
      const spdVal = document.createElement('strong');
      spdVal.textContent = data.stats.speed;
      spdSpan.appendChild(spdVal);
      statsGrid.appendChild(spdSpan);
      content.appendChild(statsGrid);

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

      const descSection = document.createElement('div');
      descSection.className = 'card-section card-description';
      descSection.style.marginTop = '16px';
      const descHeader = document.createElement('h3');
      descHeader.textContent = '説明';
      const descP = document.createElement('p');
      descP.textContent = data.description;
      descSection.append(descHeader, descP);
      content.appendChild(descSection);

      const equipSection = document.createElement('div');
      equipSection.className = 'card-section card-equipment-list';
      equipSection.style.marginTop = '16px';
      const equipHeader = document.createElement('h3');
      equipHeader.textContent = '装備中';
      equipSection.appendChild(equipHeader);

      const equippedUl = document.createElement('ul');
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
      equipSection.appendChild(equippedUl);

      const equipHeader2 = document.createElement('h3');
      equipHeader2.textContent = '装備する';
      equipSection.appendChild(equipHeader2);

      if (equipmentList.length > 0) {
        const invUl = document.createElement('ul');
        equipmentList.forEach(eq => {
          const li = document.createElement('li');
          const btn = document.createElement('button');
          btn.className = 'equip-btn';
          btn.dataset.equipId = eq.id;
          btn.dataset.idx = data.index;
          btn.textContent = '装備';
          li.textContent = eq.name + ' ';
          li.appendChild(btn);
          invUl.appendChild(li);
        });
        equipSection.appendChild(invUl);
      } else {
        const p = document.createElement('p');
        p.textContent = '装備を持っていない。';
        equipSection.appendChild(p);
      }

      content.appendChild(equipSection);
      modalCardBody.appendChild(content);
      modal.classList.add('show');
      modal.focus();
      modalCardBody.querySelectorAll('.equip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          btn.disabled = true;
          const equipId = btn.dataset.equipId;
          const idx = btn.dataset.idx;
          fetch(equipUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ equip_id: equipId, monster_idx: idx })
          })
          .then(res => res.json())
          .then(resp => {
            if (resp.success) {
              equipmentList.length = 0;
              resp.equipment_inventory.forEach(e => equipmentList.push(e));
              data.equipment = resp.monster_equipment;
              if (resp.monster_stats) {
                data.stats = resp.monster_stats;
              }
              displayMonsterDetails(data);
            }
          })
          .catch(() => alert('装備の更新に失敗しました'))
          .finally(() => {
            btn.disabled = false;
          });
        });
      });
      modalCardBody.querySelectorAll('.unequip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          btn.disabled = true;
          const idx = btn.dataset.idx;
          const slot = btn.dataset.slot;
          fetch(equipUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ equip_id: null, monster_idx: idx, slot: slot })
          })
          .then(res => res.json())
          .then(resp => {
            if (resp.success) {
              equipmentList.length = 0;
              resp.equipment_inventory.forEach(e => equipmentList.push(e));
              data.equipment = resp.monster_equipment;
              if (resp.monster_stats) {
                data.stats = resp.monster_stats;
              }
              displayMonsterDetails(data);
            }
          })
          .catch(() => alert('装備の更新に失敗しました'))
          .finally(() => {
            btn.disabled = false;
          });
        });
      });
    }

    function closeModal() {
      modal.classList.remove('show');
    }

    modal.querySelector('.modal-close-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', (event) => {
      if (event.target === modal) {
        closeModal();
      }
    });
    modal.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeModal();
      }
    });
  });
