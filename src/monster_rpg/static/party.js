  window.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.fade-in').classList.add('show');
    const modal = document.getElementById('monster-detail-modal');
    const modalCardBody = document.getElementById('modal-card-body');
    const partyMembers = document.querySelectorAll('.party-member');
    const equipmentList = {{ equipment_list|tojson|safe }};
    const equipUrl = "{{ url_for('equip', user_id=user_id) }}";
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
      let skillsHtml = '';
      if (data.skills && data.skills.length > 0) {
        skillsHtml = `<ul>${data.skills.map(skill => `<li><strong>${skill.name}</strong>: ${skill.description}</li>`).join('')}</ul>`;
      } else {
        skillsHtml = '<p>覚えているスキルはない。</p>';
      }

      const expNeeded = data.exp_to_next - data.exp;
      let equippedHtml = '<ul>';
      (data.equipment_slots || []).forEach(slot => {
        const name = data.equipment && data.equipment[slot] ? data.equipment[slot] : '空き';
        const btn = data.equipment && data.equipment[slot] ? ` <button class="unequip-btn" data-slot="${slot}" data-idx="${data.index}">外す</button>` : '';
        equippedHtml += `<li>${slot}: ${name}${btn}</li>`;
      });
      equippedHtml += '</ul>';

      let equipListHtml = '';
      if (equipmentList.length > 0) {
        equipListHtml = '<ul>' + equipmentList.map(eq => `<li>${eq.name} <button class="equip-btn" data-equip-id="${eq.id}" data-idx="${data.index}">装備</button></li>`).join('') + '</ul>';
      } else {
        equipListHtml = '<p>装備を持っていない。</p>';
      }

      modalCardBody.innerHTML = `
        <div class="card-image-area">
          <img src="${data.image}" alt="${data.name}" class="card-monster-img">
        </div>

        <div class="card-header">
            <h2 class="card-monster-name">${data.name}</h2>
            <div class="card-monster-lvhp">
                <span>Lv. ${data.level}</span> | <span>HP: ${data.hp} / ${data.max_hp}</span> | <span>EXP: ${data.exp} / ${data.exp_to_next} (残り ${expNeeded})</span>
            </div>
        </div>
        
        <div class="card-content">
            <div class="card-stats-grid">
              <span>こうげき: <strong>${data.stats.attack}</strong></span>
              <span>ぼうぎょ: <strong>${data.stats.defense}</strong></span>
              <span>すばやさ: <strong>${data.stats.speed}</strong></span>
            </div>
    
            <div class="card-section card-skills-list">
                <h3>スキル</h3>
                ${skillsHtml}
            </div>
            
            <div class="card-section card-description" style="margin-top: 16px;">
                <h3>説明</h3>
                <p>${data.description}</p>
            </div>
            <div class="card-section card-equipment-list" style="margin-top: 16px;">
                <h3>装備中</h3>
                ${equippedHtml}
                <h3>装備する</h3>
                ${equipListHtml}
            </div>
        </div>
      `;
      modal.classList.add('show');
      modalCardBody.querySelectorAll('.equip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
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
              displayMonsterDetails(data);
            }
          });
        });
      });
      modalCardBody.querySelectorAll('.unequip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
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
              displayMonsterDetails(data);
            }
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
  });
