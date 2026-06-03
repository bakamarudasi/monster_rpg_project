/* =====================================================================
   トースト通知（全ページ共通）
   - window.showToast(message, type, opts) でいつでも表示可能
   - サーバ側の flash() メッセージ(#flash-data)をロード時に自動表示
   type: info | success | level | item | save | warn | error
   ===================================================================== */
(function () {
    const ICONS = {
        info: 'ℹ️', success: '✅', level: '🎉',
        item: '🎁', save: '💾', warn: '⚠️', error: '⛔'
    };

    function ensureContainer() {
        let c = document.getElementById('toast-container');
        if (!c) {
            c = document.createElement('div');
            c.id = 'toast-container';
            c.className = 'toast-container';
            document.body.appendChild(c);
        }
        return c;
    }

    window.showToast = function (message, type, opts) {
        opts = opts || {};
        if (!message) return;
        const container = ensureContainer();

        const toast = document.createElement('div');
        toast.className = 'toast toast-' + (type || 'info');

        const icon = ICONS[type];
        if (icon) {
            const ico = document.createElement('span');
            ico.className = 'toast-icon';
            ico.textContent = icon;
            toast.appendChild(ico);
        }
        const msg = document.createElement('span');
        msg.className = 'toast-msg';
        msg.textContent = message;
        toast.appendChild(msg);

        container.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('show'));

        const remove = () => {
            toast.classList.remove('show');
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 350);
        };
        const timer = setTimeout(remove, opts.duration || 3200);
        toast.addEventListener('click', () => { clearTimeout(timer); remove(); });
    };

    /* サーバからの flash メッセージを表示 */
    document.addEventListener('DOMContentLoaded', function () {
        const data = document.getElementById('flash-data');
        if (!data) return;
        let msgs = [];
        try { msgs = JSON.parse(data.textContent || '[]'); } catch (e) { return; }
        msgs.forEach(m => window.showToast(m.message, m.category || 'info'));
    });
})();
