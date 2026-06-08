  window.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.fade-in').classList.add('show');
    const modal = document.getElementById('monster-detail-modal');
    const modalCardBody = document.getElementById('modal-card-body');
    const partyMembers = document.querySelectorAll('.party-member');

    let equipmentList = [];
    let equipUrl = '';
    let appraiseUrl = '';

    /* 装備の対現状差分（±）を色分けして返す */
    const DIFF_LABELS = [['attack','攻'],['defense','防'],['magic','魔'],['magic_defense','魔防'],['speed','速'],['critical_rate','会心'],['evasion_rate','回避']];
    const PERCENT_STATS = { critical_rate: 1, evasion_rate: 1 };
    function buildEquipDiff(cand, equipped) {
      const wrap = document.createElement('span');
      wrap.className = 'equip-diff';
      DIFF_LABELS.forEach(([k, lab]) => {
        const c = (cand && cand[k]) || 0;
        const e = (equipped && equipped[k]) || 0;
        if (c === 0 && e === 0) return;
        const d = c - e;
        const s = document.createElement('span');
        s.className = 'diff ' + (d > 0 ? 'up' : (d < 0 ? 'down' : 'same'));
        const unit = PERCENT_STATS[k] ? '%' : '';
        s.textContent = lab + (d > 0 ? '+' : '') + d + unit;
        wrap.appendChild(s);
      });
      return wrap;
    }
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';
    const dataElem = document.getElementById('party-data');
    if (dataElem) {
      try {
        const parsed = JSON.parse(dataElem.textContent);
        equipmentList = parsed.equipment_list || [];
        equipUrl = parsed.equip_url || '';
        appraiseUrl = parsed.appraise_url || '';
      } catch (e) {
        console.error('Failed to parse party-data', e);
      }
    }

    function appraiseMonster(data, btn) {
      if (!appraiseUrl) return;
      btn.disabled = true;
      fetch(appraiseUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ monster_idx: data.index })
      })
        .then(res => res.json())
        .then(resp => {
          if (resp.success) {
            data.individuality = resp.individuality;
            displayMonsterDetails(data);
            if (typeof window.showToast === 'function' && !resp.already) {
              window.showToast('🔍 鑑定完了！', 'item', { duration: 2500 });
            }
          } else {
            alert(resp.error || '鑑定に失敗しました');
            btn.disabled = false;
          }
        })
        .catch(() => { alert('鑑定に失敗しました'); btn.disabled = false; });
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

      if (data.individuality) {
        const ind = data.individuality;
        const indiv = document.createElement('div');
        indiv.className = 'card-monster-individuality';
        const p = ind.personality;
        const t = ind.talent;
        if (p) {
          const pTag = document.createElement('span');
          pTag.className = 'indiv-tag indiv-personality';
          pTag.textContent = '性格: ' + p.name + (p.effect ? '（' + p.effect + '）' : '');
          indiv.appendChild(pTag);
        }
        if (t) {
          const tTag = document.createElement('span');
          tTag.className = 'indiv-tag indiv-talent' + (t.hidden ? ' indiv-talent-hidden' : '');
          tTag.textContent = (t.hidden ? '🌟才能: ' : '才能: ') + t.name;
          indiv.appendChild(tTag);
        }
        const tr = ind.trait;
        if (tr) {
          const trTag = document.createElement('span');
          trTag.className = 'indiv-tag indiv-trait';
          trTag.textContent = '✦特性: ' + tr.name;
          if (tr.description) trTag.title = tr.description;
          indiv.appendChild(trTag);
        }
        header.appendChild(indiv);

        // 個体値（鑑定済みのときだけ数値を表示）
        const ivBox = document.createElement('div');
        ivBox.className = 'card-monster-ivs';
        if (ind.appraised && ind.ivs) {
          const title = document.createElement('div');
          title.className = 'iv-title';
          title.textContent = '個体値 ' + (ind.iv_total != null ? '(' + ind.iv_total + '/' + ind.iv_max + ')' : '');
          ivBox.appendChild(title);
          const grid = document.createElement('div');
          grid.className = 'iv-grid';
          const labels = { hp: 'HP', attack: '攻', defense: '防', magic: '魔', speed: '速' };
          ['hp', 'attack', 'defense', 'magic', 'speed'].forEach(s => {
            if (!ind.ivs[s]) return;
            const cell = document.createElement('span');
            const v = ind.ivs[s].value;
            cell.className = 'iv-cell' + (v === 31 ? ' iv-best' : '');
            cell.textContent = (labels[s] || s) + ' ' + v + '（' + ind.ivs[s].label + '）';
            grid.appendChild(cell);
          });
          ivBox.appendChild(grid);
        } else {
          const hint = document.createElement('div');
          hint.className = 'iv-unappraised';
          hint.textContent = '個体値：未鑑定';
          ivBox.appendChild(hint);
          if (data.index != null && appraiseUrl) {
            const btn = document.createElement('button');
            btn.className = 'appraise-btn';
            btn.textContent = '鑑定する（50G）';
            btn.addEventListener('click', () => appraiseMonster(data, btn));
            ivBox.appendChild(btn);
          }
        }
        header.appendChild(ivBox);
      }
      modalCardBody.appendChild(header);

      const content = document.createElement('div');
      content.className = 'card-content';

      const statsGrid = document.createElement('div');
      statsGrid.className = 'card-stats-grid';
      // [ラベル, キー, 単位, 0でも表示するか]
      const statDefs = [
        ['こうげき', 'attack', '', true],
        ['ぼうぎょ', 'defense', '', true],
        ['まりょく', 'magic', '', true],
        ['まぼう', 'magic_defense', '', true],
        ['すばやさ', 'speed', '', true],
        ['かいしん', 'critical_rate', '%', false],
        ['かいひ', 'evasion_rate', '%', false],
      ];
      statDefs.forEach(([label, key, unit, showZero]) => {
        const v = data.stats[key];
        if (v === undefined || v === null) return;
        if (!showZero && !v) return;   // 会心/回避は0なら省く
        const span = document.createElement('span');
        span.textContent = label + ': ';
        const strong = document.createElement('strong');
        strong.textContent = v + unit;
        span.appendChild(strong);
        statsGrid.appendChild(span);
      });
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
          /* 現在その枠に着けている装備との差分（±）を色分け表示 */
          const equipped = (data.equipped_stats || {})[eq.slot];
          const diff = buildEquipDiff(eq.stats_num, equipped);
          if (diff.childNodes.length) li.appendChild(diff);
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
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify({ equip_id: equipId, monster_idx: idx })
          })
          .then(res => res.json())
          .then(resp => {
            if (resp.success) {
              equipmentList.length = 0;
              resp.equipment_inventory.forEach(e => equipmentList.push(e));
              data.equipment = resp.monster_equipment;
              if (resp.equipped_stats) { data.equipped_stats = resp.equipped_stats; }
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
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify({ equip_id: null, monster_idx: idx, slot: slot })
          })
          .then(res => res.json())
          .then(resp => {
            if (resp.success) {
              equipmentList.length = 0;
              resp.equipment_inventory.forEach(e => equipmentList.push(e));
              data.equipment = resp.monster_equipment;
              if (resp.equipped_stats) { data.equipped_stats = resp.equipped_stats; }
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
