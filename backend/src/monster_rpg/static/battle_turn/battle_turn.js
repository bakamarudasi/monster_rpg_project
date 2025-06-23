function setupBattleUI() {
    /* HPバーのアニメーション */
    document.querySelectorAll('.hp-fill').forEach(fill => {
        const finalWidth = fill.style.width;
        fill.style.width = '0%';
        requestAnimationFrame(() => {
            fill.style.transition = 'width 1s cubic-bezier(0.25, 1, 0.5, 1)';
            fill.style.width = finalWidth;
        });
    });

    /* HP低下時の点滅 */
    document.querySelectorAll('.hp-fill.critical').forEach(el => el.classList.add('blink'));

    /* 倒れたメンバーをフェードアウト */
    document.querySelectorAll('.battle-unit.down').forEach(el => {
        el.style.transition = 'opacity 0.8s ease, filter 0.8s ease';
        el.style.opacity = '0.4';
        if(el.classList.contains('enemy')) {
            el.style.filter = 'grayscale(80%)';
        }
    });

    /* ターゲット選択の表示切り替え */
    function updateTargets() {
        const actionSel = document.getElementById('action');
        if (!actionSel) return;
        const enemySel = document.querySelector('select[name="target_enemy"]');
        const allySel = document.querySelector('select[name="target_ally"]');
        const itemSel = document.querySelector('select[name="item_idx"]');
        const opt = actionSel.selectedOptions[0];
        const target = opt.dataset.target || 'enemy';
        const scope = opt.dataset.scope || 'single';

        const isItem = opt.value === 'item';
        const skillUI = document.getElementById('skill-ui');
        if (skillUI) skillUI.style.display = opt.value === 'skill' ? '' : 'none';

        if (target === 'none' || scope === 'all') {
            enemySel.style.display = 'none';
            allySel.style.display = 'none';
            if (itemSel) itemSel.style.display = 'none';
        } else if (target === 'ally') {
            enemySel.style.display = 'none';
            allySel.style.display = '';
            if (itemSel) itemSel.style.display = isItem ? '' : 'none';
        } else {
            enemySel.style.display = '';
            allySel.style.display = 'none';
            if (itemSel) itemSel.style.display = 'none';
        }
    }
    const actionSel = document.getElementById('action');
    if (actionSel) {
        actionSel.addEventListener('change', updateTargets);
        updateTargets();
    }
    window.updateTargets = updateTargets;

    /* 現在のHP/MPをdata属性に保存 */
    document.querySelectorAll('.battle-unit').forEach(unit => {
        const hpText = unit.querySelector('.hp-text');
        if (hpText) {
            const hp = parseInt(hpText.textContent.split('/')[0]);
            if (!isNaN(hp)) unit.dataset.hp = hp;
        }
        const mpText = unit.querySelector('.mp-text');
        if (mpText) {
            const mp = parseInt(mpText.textContent.split('/')[0]);
            if (!isNaN(mp)) unit.dataset.mp = mp;
        }
    });

    /* 敵詳細パネルの表示 */
    const detailPanel = document.getElementById('enemy-detail');
    const closeBtn = detailPanel.querySelector('.close-btn');
    const fields = {
        name: document.getElementById('detail-name'),
        level: document.getElementById('detail-level'),
        hp: document.getElementById('detail-hp'),
        maxHp: document.getElementById('detail-max-hp'),
        mp: document.getElementById('detail-mp'),
        maxMp: document.getElementById('detail-max-mp'),
        attack: document.getElementById('detail-attack'),
        defense: document.getElementById('detail-defense'),
        speed: document.getElementById('detail-speed'),
        statuses: document.getElementById('detail-statuses'),
    };
    document.querySelectorAll('.enemy.battle-unit').forEach(el => {
        el.addEventListener('click', () => {
            for (const key in fields) {
                const dataKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
                fields[key].textContent = el.dataset[dataKey] || '';
            }
            try {
                const list = JSON.parse(el.dataset.statuses || '[]');
                fields.statuses.textContent = list.map(s => `${s.display}(${s.remaining})`).join('、');
            } catch (e) {
                fields.statuses.textContent = '';
            }
            detailPanel.classList.add('open');
        });
    });
    closeBtn.addEventListener('click', () => detailPanel.classList.remove('open'));

    /* --- AJAXでコマンド送信 --- */
    const form = document.querySelector('.command-window form');
    if (form) {
        form.addEventListener('submit', evt => {
            evt.preventDefault();
            const formData = new FormData(form);
            const postUrl = form.getAttribute('action');  // use the form's action URL
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = true;

            const payload = Object.fromEntries(formData.entries());
            fetch(postUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
                .then(resp => resp.json())
                .then(data => {
                    if (data.finished) {
                        document.open();
                        document.write(data.html);
                        document.close();
                        return;
                    }
                    applyBattleData(data);
                })
                .catch(err => {
                    console.error('Fetch error', err);
                    alert('通信エラーが発生しました');
                })
                .finally(() => {
                    if (submitBtn) submitBtn.disabled = false;
                });
        });
    }

    const cmdWindow = document.querySelector('.command-window');
    // Disabled auto scrolling to keep the battle screen position
    // if (cmdWindow) cmdWindow.scrollIntoView({behavior: 'smooth'});
}

function updateUnitList(units, infoList) {
    infoList.forEach((info, idx) => {
        const unit = units[idx];
        if (!unit) return;
        const prevHp = parseInt(unit.dataset.hp || '0');
        unit.dataset.hp = info.hp;
        unit.dataset.mp = info.mp;
        unit.dataset.statuses = JSON.stringify(info.status_effects || []);
        if (!info.alive) unit.classList.add('down');
        const fill = unit.querySelector('.hp-fill');
        const pct = Math.round(info.hp / info.max_hp * 100);
        if (fill) {
            fill.classList.remove('low', 'critical');
            if (pct <= 25) {
                fill.classList.add('critical');
            } else if (pct <= 50) {
                fill.classList.add('low');
            }
            fill.style.width = pct + '%';
        }
        const text = unit.querySelector('.hp-text');
        if (text) text.textContent = info.hp + '/' + info.max_hp;

        const mpFill = unit.querySelector('.mp-fill');
        const mpPct = info.max_mp > 0 ? Math.round(info.mp / info.max_mp * 100) : 0;
        if (mpFill) {
            mpFill.style.width = mpPct + '%';
        }
        const mpText = unit.querySelector('.mp-text');
        if (mpText) mpText.textContent = info.mp + '/' + info.max_mp;

        if (!isNaN(prevHp) && info.hp < prevHp) {
            showPopupIndicator(unit, '-' + (prevHp - info.hp), 'damage-indicator');
        } else if (!isNaN(prevHp) && info.hp > prevHp) {
            showPopupIndicator(unit, '+' + (info.hp - prevHp), 'heal-indicator');
        }
    });
}

function buildSkillUI(actor) {
    const tabsContainer = document.getElementById('skill-tabs');
    const panelsContainer = document.getElementById('skill-panels');
    const descArea = document.getElementById('skill-desc');
    const hiddenInput = document.getElementById('selected-skill-id');
    const actionSel = document.getElementById('action');
    if (!tabsContainer || !panelsContainer || !descArea || !hiddenInput) return;

    tabsContainer.textContent = '';
    panelsContainer.textContent = '';
    descArea.textContent = '';
    hiddenInput.value = '';

    if (!actor || !Array.isArray(actor.skills)) return;

    const groups = {};
    actor.skills.forEach((sk, idx) => {
        const type = sk.skill_type || 'その他';
        if (!groups[type]) groups[type] = [];
        const copy = Object.assign({ index: idx }, sk);
        groups[type].push(copy);
    });

    const groupEntries = Object.entries(groups);
    groupEntries.forEach(([type, skills], i) => {
        const tab = document.createElement('button');
        tab.className = 'skill-tab';
        tab.textContent = type;
        if (i === 0) tab.classList.add('active');
        tabsContainer.appendChild(tab);

        const panel = document.createElement('div');
        panel.className = 'skill-panel';
        if (i !== 0) panel.classList.add('hidden');
        skills.forEach(sk => {
            const btn = document.createElement('button');
            btn.className = 'skill-btn';
            btn.textContent = sk.name + (sk.cost ? ` (MP:${sk.cost})` : '');
            const unitEl = document.querySelector(`[data-unit-id="${actor.unit_id}"]`);
            const mp = unitEl ? parseInt(unitEl.dataset.mp || '0') : 0;
            if (sk.cost && mp < sk.cost) {
                btn.disabled = true;
                btn.classList.add('disabled');
            }
            btn.addEventListener('click', () => {
                panelsContainer.querySelectorAll('.skill-btn.selected').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                hiddenInput.value = sk.index;
                descArea.textContent = sk.description || '';
                const opt = actionSel ? actionSel.querySelector('option[value="skill"]') : null;
                if (opt) {
                    opt.dataset.target = sk.target || 'enemy';
                    opt.dataset.scope = sk.scope || 'single';
                }
                if (actionSel) {
                    actionSel.value = 'skill';
                    updateTargets();
                }
            });
            panel.appendChild(btn);
        });
        panelsContainer.appendChild(panel);

        tab.addEventListener('click', () => {
            tabsContainer.querySelectorAll('.skill-tab').forEach(t => t.classList.remove('active'));
            panelsContainer.querySelectorAll('.skill-panel').forEach(p => p.classList.add('hidden'));
            tab.classList.add('active');
            panel.classList.remove('hidden');
        });
    });
}

function applyBattleData(data) {
    const detailPanel = document.getElementById('enemy-detail');
    if (detailPanel) detailPanel.classList.remove('open');
    const allyUnits = document.querySelectorAll('.ally-party-display .battle-unit');
    allyUnits.forEach(el => el.classList.remove('active-turn'));
    updateUnitList(allyUnits, data.hp_values.player);

    const enemyUnits = document.querySelectorAll('.enemy-area .battle-unit');
    updateUnitList(enemyUnits, data.hp_values.enemy);

    const logEl = document.querySelector('.log');
    if (logEl) {
        logEl.textContent = '';
        data.log.forEach(entry => {
            const li = document.createElement('li');
            li.textContent = entry.message;
            li.className = 'log-message-' + entry.type;
            logEl.appendChild(li);
        });
    }

    const banner = document.querySelector('.turn-banner');
    if (banner) banner.textContent = 'Turn ' + data.turn;

    if (data.current_actor) {
        const label = document.querySelector('label[for="action"]');
        const actionSel = document.getElementById('action');
        if (label) label.textContent = data.current_actor.name + ':';
        if (actionSel) {
            actionSel.textContent = '';
            const atkOpt = document.createElement('option');
            atkOpt.value = 'attack';
            atkOpt.dataset.target = 'enemy';
            atkOpt.dataset.scope = 'single';
            atkOpt.textContent = '攻撃';
            actionSel.appendChild(atkOpt);

            const skillOpt = document.createElement('option');
            skillOpt.value = 'skill';
            skillOpt.dataset.target = 'enemy';
            skillOpt.dataset.scope = 'single';
            skillOpt.textContent = 'スキル';
            actionSel.appendChild(skillOpt);

            const itemOpt = document.createElement('option');
            itemOpt.value = 'item';
            itemOpt.dataset.target = 'ally';
            itemOpt.dataset.scope = 'single';
            itemOpt.textContent = 'アイテム';
            actionSel.appendChild(itemOpt);

            const scoutOpt = document.createElement('option');
            scoutOpt.value = 'scout';
            scoutOpt.dataset.target = 'enemy';
            scoutOpt.dataset.scope = 'single';
            scoutOpt.textContent = 'スカウト';
            actionSel.appendChild(scoutOpt);

            const runOpt = document.createElement('option');
            runOpt.value = 'run';
            runOpt.dataset.target = 'none';
            runOpt.dataset.scope = 'none';
            runOpt.textContent = '逃げる';
            actionSel.appendChild(runOpt);

            updateTargets();
        }

        const activeUnit = Array.from(allyUnits).find(u => u.dataset.unitId === data.current_actor.unit_id);
        if (activeUnit) activeUnit.classList.add('active-turn');

        buildSkillUI(data.current_actor);
    }

    const cmdWindow = document.querySelector('.command-window');
    // Disabled auto scrolling to keep the battle screen position
    // if (cmdWindow) cmdWindow.scrollIntoView({behavior: 'smooth'});
}

function showPopupIndicator(container, text, className) {
    const popup = document.createElement('div');
    popup.className = className;
    popup.textContent = text;
    container.appendChild(popup);

    requestAnimationFrame(() => {
        const w = popup.offsetWidth;
        popup.style.marginLeft = -(w / 2) + 'px';
        popup.classList.add('visible');
    });

    setTimeout(() => popup.remove(), 800);
}

document.addEventListener('DOMContentLoaded', () => {
    setupBattleUI();
    const form = document.querySelector('.command-window form');
    if (form) {
        const m = form.getAttribute('action').match(/\/battle\/(\d+)/);
        if (m) {
            fetch(`/battle/${m[1]}`)
                .then(resp => resp.json())
                .then(data => applyBattleData(data))
                .catch(err => console.error('Fetch error', err));
        }
    }
});
