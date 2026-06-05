(() => {
    /* --- オート/倍速 戦闘の状態と共通送信 --- */
    let battlePostUrl = null;
    let battleCsrf = null;
    let autoMode = false;
    let fastMode = false;
    let lastData = null;

    function sendBattleAction(payload) {
        if (!battlePostUrl) return;
        if (payload.action === 'skill' && payload.selected_skill_id) {
            payload.action = 'skill' + payload.selected_skill_id;
        }
        const submitBtn = document.querySelector('.command-window form button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        fetch(battlePostUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': battleCsrf },
            body: JSON.stringify(payload)
        })
            .then(resp => { if (!resp.ok) throw new Error(`HTTP ${resp.status}`); return resp.json(); })
            .then(data => {
                if (data.finished) { document.open(); document.write(data.html); document.close(); return; }
                applyBattleData(data);
            })
            .catch(err => { console.error('Fetch error', err); alert(`通信エラー: ${err.message}`); })
            .finally(() => { if (submitBtn) submitBtn.disabled = false; });
    }

    /* プレイヤーのターンでオートONなら、行動者の性格に応じた行動をサーバ側で選ぶ */
    function maybeAutoAct(data) {
        if (!autoMode || !data || data.finished || !data.current_actor) return;
        const delay = fastMode ? 120 : 450;
        setTimeout(() => {
            if (autoMode) sendBattleAction({ action: 'auto' });
        }, delay);
    }

    /* 属性相性: その属性が「弱い」相手（弱点を突かれる側）。backend の elements.py と対応 */
    const ELEMENT_WEAKNESS = {
        '火': '水', '風': '火', '水': '風',
        '氷': '火', '雷': '土', '土': '風',
        '毒': '風', '光': '闇', '闇': '光'
    };

    /* フィールド(天候)バナーの更新 */
    function updateFieldBanner(field) {
        const banner = document.getElementById('field-banner');
        if (!banner) return;
        if (field && field.element && field.remaining > 0) {
            const nm = field.name || (field.element + 'フィールド');
            const mult = field.multiplier ? `×${field.multiplier}` : '';
            banner.textContent = `🌐 ${nm}（${field.element}属性${mult} ・ 残り${field.remaining}ターン）`;
            banner.dataset.element = field.element;
            banner.classList.remove('hidden');
        } else {
            banner.textContent = '';
            banner.removeAttribute('data-element');
            banner.classList.add('hidden');
        }
    }

    /* 戦闘ログの新規分からトーストを出す（重複防止に長さを記録） */
    let lastLogLen = -1;
    function toastFromLog(log) {
        if (!Array.isArray(log) || typeof window.showToast !== 'function') return;
        if (lastLogLen < 0) { lastLogLen = log.length; return; } /* 初回は履歴を出さない */
        const fresh = log.slice(lastLogLen);
        lastLogLen = log.length;
        fresh.forEach(e => {
            const m = e.message || '';
            if (e.type === 'item_drop') {
                window.showToast(m, 'item');
            } else if (m.indexOf('上がった') !== -1 && m.indexOf('レベル') !== -1) {
                window.showToast(m.replace(/🎉/g, '').trim(), 'level');
            } else if (m.indexOf('join your party') !== -1) {
                window.showToast('仲間が増えた！', 'success');
            }
        });
    }

    function buildUnitElement(info, idx, side) {
        const unit = document.createElement('div');
        unit.className = `battle-unit ${side}`;
        if (!info.alive) unit.classList.add('down');
        if (info.is_boss) unit.classList.add('boss');
        unit.dataset.unitId = `${side}-${idx}`;
        unit.dataset.name = info.name;
        unit.dataset.level = info.level;
        unit.dataset.hp = info.hp;
        unit.dataset.maxHp = info.max_hp;
        unit.dataset.mp = info.mp;
        unit.dataset.maxMp = info.max_mp;
        unit.dataset.attack = info.attack;
        unit.dataset.defense = info.defense;
        unit.dataset.speed = info.speed;
        if (info.element) unit.dataset.element = info.element;
        unit.dataset.statuses = JSON.stringify(info.statuses || []);
        /* 個性（詳細パネル用のデータ属性） */
        if (info.personality) {
            unit.dataset.personality = info.personality.name || '';
            unit.dataset.personalityEffect = info.personality.effect || '';
        }
        if (info.talent && info.talent.id !== 'common') unit.dataset.talent = info.talent.name || '';
        if (info.trait) {
            unit.dataset.trait = info.trait.name || '';
            unit.dataset.traitDesc = info.trait.description || '';
        }

        if (info.image) {
            const img = document.createElement('img');
            img.className = 'unit-img';
            img.src = info.image;
            img.alt = info.name;
            unit.appendChild(img);
        }

        const infoBox = document.createElement('div');
        infoBox.className = 'member-info';
        const nm = document.createElement('div');
        nm.className = 'member-name';
        if (info.is_boss) {
            const badge = document.createElement('span');
            badge.className = 'boss-badge';
            badge.textContent = 'BOSS';
            nm.appendChild(badge);
        }
        nm.appendChild(document.createTextNode(info.name));
        infoBox.appendChild(nm);

        /* 性格・才能をカード上にも小さく表示（味方はタップ詳細が無いため） */
        const tags = document.createElement('div');
        tags.className = 'unit-tags';
        if (info.personality) {
            const p = document.createElement('span');
            p.className = 'unit-pers';
            p.textContent = info.personality.name;
            if (info.personality.effect) p.title = '性格：' + info.personality.effect;
            tags.appendChild(p);
        }
        if (info.talent && info.talent.id !== 'common') {
            const t = document.createElement('span');
            t.className = 'unit-talent' + (info.talent.hidden ? ' hidden' : '');
            t.textContent = info.talent.name;
            t.title = '才能';
            tags.appendChild(t);
        }
        if (tags.childNodes.length) infoBox.appendChild(tags);

        const hpBar = document.createElement('div');
        hpBar.className = 'hp-bar';
        const hpFill = document.createElement('div');
        hpFill.className = 'hp-fill';
        const pct = Math.round(info.hp / info.max_hp * 100);
        if (pct <= 25) hpFill.classList.add('critical');
        else if (pct <= 50) hpFill.classList.add('low');
        hpFill.style.width = pct + '%';
        hpBar.appendChild(hpFill);
        infoBox.appendChild(hpBar);

        const mpBar = document.createElement('div');
        mpBar.className = 'mp-bar';
        const mpFill = document.createElement('div');
        mpFill.className = 'mp-fill';
        const mpPct = info.max_mp > 0 ? Math.round(info.mp / info.max_mp * 100) : 0;
        mpFill.style.width = mpPct + '%';
        mpBar.appendChild(mpFill);

        infoBox.appendChild(mpBar);
        unit.appendChild(infoBox);

        const hpText = document.createElement('div');
        hpText.className = 'hp-text';
        hpText.textContent = info.hp + '/' + info.max_hp;
        unit.appendChild(hpText);

        const mpText = document.createElement('div');
        mpText.className = 'mp-text';
        mpText.textContent = info.mp + '/' + info.max_mp;
        unit.appendChild(mpText);

        const shieldText = document.createElement('div');
        shieldText.className = 'shield-text';
        const sh = info.shield || 0;
        shieldText.textContent = sh > 0 ? '🛡' + sh : '';
        if (sh <= 0) shieldText.classList.add('hidden');
        unit.appendChild(shieldText);
        unit.dataset.shield = sh;

        return unit;
    }

    function populatePartyAreas(data) {
        const enemyArea = document.getElementById('enemy-party-area');
        const allyArea = document.getElementById('ally-party-area');
        if (enemyArea && Array.isArray(data.enemy_info)) {
            enemyArea.textContent = '';
            data.enemy_info.forEach((e, i) => enemyArea.appendChild(buildUnitElement(e, i, 'enemy')));
        }
        if (allyArea && Array.isArray(data.ally_info)) {
            allyArea.textContent = '';
            data.ally_info.forEach((a, i) => allyArea.appendChild(buildUnitElement(a, i, 'ally')));
        }

        const enemySel = document.querySelector('select[name="target_enemy"]');
        const allySel = document.querySelector('select[name="target_ally"]');
        const itemSel = document.querySelector('select[name="item_idx"]');
        if (enemySel && Array.isArray(data.enemy_info)) {
            enemySel.textContent = '';
            data.enemy_info.forEach((e, i) => {
                const opt = document.createElement('option');
                opt.value = i;
                opt.textContent = e.name;
                enemySel.appendChild(opt);
            });
        }
        if (allySel && Array.isArray(data.ally_info)) {
            allySel.textContent = '';
            data.ally_info.forEach((a, i) => {
                const opt = document.createElement('option');
                opt.value = i;
                opt.textContent = a.name;
                allySel.appendChild(opt);
            });
        }
        if (itemSel && Array.isArray(data.items)) {
            itemSel.textContent = '';
            data.items.forEach((it, i) => {
                const opt = document.createElement('option');
                opt.value = i;
                opt.textContent = it.name;
                itemSel.appendChild(opt);
            });
        }
    }

    function updateTurnOrder(list) {
        const bar = document.getElementById('turn-order-bar');
        if (!bar) return;
        bar.textContent = '';
        list.forEach(id => {
            const unit = document.querySelector(`[data-unit-id="${id}"]`);
            if (!unit) return;
            const img = unit.querySelector('.unit-img');
            if (img) {
                const icon = img.cloneNode(true);
                icon.classList.add('turn-order-icon');
                bar.appendChild(icon);
            } else {
                const span = document.createElement('span');
                span.textContent = unit.dataset.name || id;
                bar.appendChild(span);
            }
        });
    }

    function buildActionUI(data) {
        const actionSel = document.getElementById('action');
        if (actionSel) {
            actionSel.textContent = '';
        }

        const defs = [
            {val:'attack', txt:'攻撃', target:'enemy', scope:'single'},
            {val:'skill',  txt:'スキル', target:'enemy', scope:'single'},
            {val:'item',   txt:'アイテム', target:'ally', scope:'single'},
            {val:'scout',  txt:'スカウト', target:'enemy', scope:'single'},
            {val:'run',    txt:'逃げる', target:'none', scope:'none'}
        ];

        const actionsPanel = document.getElementById('tab-actions');
        if (actionsPanel) actionsPanel.textContent = '';

        defs.forEach(d => {
            if (actionSel) {
                const opt = document.createElement('option');
                opt.value = d.val;
                opt.dataset.target = d.target;
                opt.dataset.scope = d.scope;
                opt.textContent = d.txt;
                actionSel.appendChild(opt);
            }

            if (actionsPanel && ['attack','scout','run'].includes(d.val)) {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.textContent = d.txt;
                btn.addEventListener('click', () => {
                    if (actionSel) {
                        actionSel.value = d.val;
                        if (actionSel.tagName !== 'SELECT') {
                            actionSel.dataset.target = d.target;
                            actionSel.dataset.scope = d.scope;
                        }
                    }
                    updateTargets();
                });
                actionsPanel.appendChild(btn);
            }
        });

        const itemsPanel = document.getElementById('tab-items');
        const itemSel = document.querySelector('select[name="item_idx"]');
        const itemsTabBtn = document.querySelector('.tab-buttons [data-panel="tab-items"]');
        if (itemsPanel && itemSel && Array.isArray(data.items) && data.items.length > 0) {
            if (itemsTabBtn) itemsTabBtn.style.display = '';
            itemsPanel.classList.remove('hidden');
            itemsPanel.textContent = '';
            itemSel.textContent = '';
            data.items.forEach((it,i) => {
                const opt = document.createElement('option');
                opt.value = i;
                opt.textContent = it.name;
                itemSel.appendChild(opt);

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.textContent = it.name;
                btn.addEventListener('click', () => {
                    if (actionSel) {
                        actionSel.value = 'item';
                        if (actionSel.tagName !== 'SELECT') {
                            actionSel.dataset.target = 'ally';
                            actionSel.dataset.scope = 'single';
                        }
                    }
                    itemSel.value = i;
                    updateTargets();
                });
                itemsPanel.appendChild(btn);
            });
        } else {
            if (itemsPanel) itemsPanel.classList.add('hidden');
            if (itemsTabBtn) itemsTabBtn.style.display = 'none';
        }
    }

    function selectTabs() {
        const buttons = document.querySelectorAll('.tab-buttons .tab-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
                btn.classList.add('active');
                const panel = document.getElementById(btn.dataset.panel);
                if (panel) panel.classList.add('active');
            });
        });
    }

    function updateTargets() {
        const actionSel = document.getElementById('action');
        if (!actionSel) return;
        const enemySel = document.querySelector('select[name="target_enemy"]');
        const allySel = document.querySelector('select[name="target_ally"]');
        const itemSel = document.querySelector('select[name="item_idx"]');

        let actionVal = actionSel.value;
        let target = 'enemy';
        let scope = 'single';
        if (actionSel.tagName === 'SELECT') {
            const opt = actionSel.selectedOptions[0];
            if (opt) {
                target = opt.dataset.target || target;
                scope = opt.dataset.scope || scope;
                actionVal = opt.value;
            }
        } else {
            target = actionSel.dataset.target || target;
            scope = actionSel.dataset.scope || scope;
        }

        const isItem = actionVal === 'item';
        const skillUI = document.getElementById('skill-ui');
        if (skillUI) skillUI.style.display = actionVal === 'skill' ? '' : 'none';

        if (target === 'none' || scope === 'all') {
            enemySel.classList.add('hidden');
            allySel.classList.add('hidden');
            if (itemSel) itemSel.classList.add('hidden');
        } else if (target === 'ally') {
            enemySel.classList.add('hidden');
            allySel.classList.remove('hidden');
            if (itemSel) {
                if (isItem) itemSel.classList.remove('hidden');
                else itemSel.classList.add('hidden');
            }
        } else {
            enemySel.classList.remove('hidden');
            allySel.classList.add('hidden');
            if (itemSel) itemSel.classList.add('hidden');
        }
    }

    function setupBattleUI() {
        const dataElem = document.getElementById('battle-init-data');
        let initData = {};
        if (dataElem) {
            try { initData = JSON.parse(dataElem.textContent); } catch(e) { console.error(e); }
        }

        populatePartyAreas(initData);
        buildActionUI(initData);
        updateTurnOrder(initData.turn_order || []);
        updateFieldBanner(initData.field || null);
        selectTabs();

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
        const actionSel = document.getElementById('action');
        if (actionSel) {
            if (actionSel.tagName === 'SELECT') {
                actionSel.addEventListener('change', updateTargets);
            }
            updateTargets();
        }


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
            personality: document.getElementById('detail-personality'),
            talent: document.getElementById('detail-talent'),
            trait: document.getElementById('detail-trait'),
            element: document.getElementById('detail-element'),
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
                /* 属性と弱点を表示 */
                const elem = el.dataset.element || '';
                if (fields.element) fields.element.textContent = elem || '—';
                const weakEl = document.getElementById('detail-weakness');
                if (weakEl) {
                    const weak = ELEMENT_WEAKNESS[elem];
                    weakEl.textContent = weak ? weak + '属性' : '—';
                }
                /* 個性: 空欄は「—」、効果/説明はツールチップに */
                if (fields.personality) fields.personality.title = el.dataset.personalityEffect || '';
                if (fields.talent && !fields.talent.textContent) fields.talent.textContent = '—';
                if (fields.trait) {
                    if (!fields.trait.textContent) fields.trait.textContent = '—';
                    fields.trait.title = el.dataset.traitDesc || '';
                }
                detailPanel.classList.add('open');
            });
        });
        closeBtn.addEventListener('click', () => detailPanel.classList.remove('open'));

        /* --- AJAXでコマンド送信（オート/手動 共通） --- */
        const form = document.querySelector('.command-window form');
        if (form) {
            battlePostUrl = form.getAttribute('action');
            battleCsrf = (new FormData(form)).get('csrf_token');
            form.addEventListener('submit', evt => {
                evt.preventDefault();
                sendBattleAction(Object.fromEntries(new FormData(form).entries()));
            });
        }
        /* オート/倍速トグル */
        const autoBtn = document.getElementById('auto-toggle');
        if (autoBtn) autoBtn.addEventListener('click', () => {
            autoMode = !autoMode;
            autoBtn.textContent = 'オート: ' + (autoMode ? 'ON' : 'OFF');
            autoBtn.classList.toggle('on', autoMode);
            if (autoMode) maybeAutoAct(lastData);
        });
        const fastBtn = document.getElementById('fast-toggle');
        if (fastBtn) fastBtn.addEventListener('click', () => {
            fastMode = !fastMode;
            fastBtn.textContent = '倍速: ' + (fastMode ? 'ON' : 'OFF');
            fastBtn.classList.toggle('on', fastMode);
            document.body.classList.toggle('fast-battle', fastMode);
        });

        const cmdWindow = document.querySelector('.command-window');
        // Disabled auto scrolling to keep the battle screen position
        // if (cmdWindow) cmdWindow.scrollIntoView({behavior: 'smooth'});
    }

    function triggerShake(hard) {
        const page = document.querySelector('.battle-page');
        if (!page) return;
        const cls = hard ? 'shake-hard' : 'shake';
        page.classList.remove('shake', 'shake-hard');
        void page.offsetWidth; /* reflowでアニメを確実に再生 */
        page.classList.add(cls);
        setTimeout(() => page.classList.remove(cls), hard ? 520 : 370);
    }

    function updateUnitList(units, infoList, opts = {}) {
        let damaged = false;
        units.forEach((unit, idx) => {
            const info = infoList[idx];
            if (!info) return;
            const prevHp = parseInt(unit.dataset.hp || '0');
            unit.dataset.hp = info.hp;
            unit.dataset.mp = info.mp;
            unit.dataset.statuses = JSON.stringify(info.status_effects || []);
            if (!info.alive) {
                unit.classList.add('down');
            } else {
                unit.classList.remove('down');
            }
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

            const shieldText = unit.querySelector('.shield-text');
            if (shieldText) {
                const sh = info.shield || 0;
                shieldText.textContent = sh > 0 ? '🛡' + sh : '';
                shieldText.classList.toggle('hidden', sh <= 0);
                unit.dataset.shield = sh;
            }

            if (!isNaN(prevHp) && info.hp < prevHp) {
                damaged = true;
                unit.classList.add('hit-flash');
                setTimeout(() => unit.classList.remove('hit-flash'), 470);
                showPopupIndicator(unit, '-' + (prevHp - info.hp), 'damage-indicator' + (opts.crit ? ' crit' : ''));
            } else if (!isNaN(prevHp) && info.hp > prevHp) {
                showPopupIndicator(unit, '+' + (info.hp - prevHp), 'heal-indicator');
            }
        });
        return damaged;
    }

    function buildSkillUI(actor) {
        const tabsContainer = document.getElementById('skill-tabs');
        const panelsContainer = document.getElementById('skill-panels');
        const descArea = document.getElementById('skill-desc');
        const hiddenInput = document.getElementById('selected-skill-id');
        const actionSel = document.getElementById('action');
        if (!tabsContainer || !panelsContainer || !descArea || !hiddenInput) return;

        const skillsTabBtn = document.querySelector('.tab-buttons [data-panel="tab-skills"]');
        const skillsPanel = document.getElementById('tab-skills');

        if (!actor || !Array.isArray(actor.skills) || actor.skills.length === 0) {
            if (skillsTabBtn) skillsTabBtn.style.display = 'none';
            if (skillsPanel) skillsPanel.classList.add('hidden');
            tabsContainer.textContent = '';
            panelsContainer.textContent = '';
            descArea.textContent = '';
            hiddenInput.value = '';
            return;
        } else {
            if (skillsTabBtn) skillsTabBtn.style.display = '';
            if (skillsPanel) skillsPanel.classList.remove('hidden');
        }

        tabsContainer.textContent = '';
        panelsContainer.textContent = '';
        descArea.textContent = '';
        hiddenInput.value = '';

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
                btn.type = 'button';
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
        const hasCrit = Array.isArray(data.log) && data.log.some(e => e.type === 'critical');
        const hasEffective = Array.isArray(data.log) && data.log.some(e => e.type === 'effective');

        const allyUnits = document.querySelectorAll('#ally-party-area .battle-unit');
        allyUnits.forEach(el => el.classList.remove('active-turn'));
        const allyDamaged = updateUnitList(allyUnits, data.hp_values.player, { crit: hasCrit });

        const enemyUnits = document.querySelectorAll('#enemy-party-area .battle-unit');
        const enemyDamaged = updateUnitList(enemyUnits, data.hp_values.enemy, { crit: hasCrit });

        if (allyDamaged || enemyDamaged) triggerShake(hasCrit || hasEffective);

        if (data.hp_values) updateFieldBanner(data.hp_values.field);

        if (Array.isArray(data.turn_order)) {
            updateTurnOrder(data.turn_order);
        }

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
        toastFromLog(data.log);

        const banner = document.querySelector('.turn-banner');
        if (banner) banner.textContent = 'Turn ' + data.turn;

        if (data.current_actor) {
            const label = document.querySelector('label[for="action"]');
            if (label) label.textContent = data.current_actor.name + ':';

            buildActionUI(data);
            updateTargets();

            const activeUnit = Array.from(allyUnits).find(u => u.dataset.unitId === data.current_actor.unit_id);
            if (activeUnit) activeUnit.classList.add('active-turn');

            buildSkillUI(data.current_actor);

            // reset tabs to Actions when new actor's turn starts
            const buttons = document.querySelectorAll('.tab-buttons .tab-btn');
            const panels = document.querySelectorAll('.tab-panel');
            buttons.forEach(b => b.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            const firstBtn = document.querySelector('.tab-buttons .tab-btn');
            const firstPanel = document.getElementById(firstBtn ? firstBtn.dataset.panel : 'tab-actions');
            if (firstBtn) firstBtn.classList.add('active');
            if (firstPanel) firstPanel.classList.add('active');
        }

        const cmdWindow = document.querySelector('.command-window');
        // Disabled auto scrolling to keep the battle screen position
        // if (cmdWindow) cmdWindow.scrollIntoView({behavior: 'smooth'});

        /* オートONなら自分のターンを自動消化 */
        lastData = data;
        maybeAutoAct(data);
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
                // Load the current battle state without advancing the turn
                fetch(`/battle-json/${m[1]}`)
                    .then(resp => {
                        if (!resp.ok) {
                            throw new Error(`HTTP ${resp.status}`);
                        }
                        return resp.json();
                    })
                    .then(data => applyBattleData(data))
                    .catch(err => {
                        console.error('Fetch error', err);
                        alert(`通信エラー: ${err.message}`);
                    });
            }
        }
    });
})();
