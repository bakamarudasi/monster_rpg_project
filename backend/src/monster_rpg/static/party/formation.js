window.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('monster-detail-modal');
    const modalBody = document.getElementById('modal-card-body');

    function displayDetails(data) {
        modalBody.textContent = '';
        const imgArea = document.createElement('div');
        imgArea.className = 'card-image-area';
        const img = document.createElement('img');
        img.src = data.image;
        img.alt = data.name;
        img.className = 'card-monster-img';
        imgArea.appendChild(img);
        modalBody.appendChild(imgArea);

        const header = document.createElement('div');
        header.className = 'card-header';
        const h2 = document.createElement('h2');
        h2.id = 'modal-title';
        h2.className = 'card-monster-name';
        h2.textContent = data.name;
        header.appendChild(h2);
        const info = document.createElement('div');
        info.className = 'card-monster-lvhp';
        info.textContent = `Lv. ${data.level} | HP: ${data.hp} / ${data.max_hp}`;
        header.appendChild(info);
        modalBody.appendChild(header);

        const content = document.createElement('div');
        content.className = 'card-content';
        const stats = document.createElement('div');
        stats.className = 'card-stats-grid';
        ['attack','defense','speed'].forEach(key => {
            const span = document.createElement('span');
            span.textContent = `${key}: ${data.stats[key]}`;
            stats.appendChild(span);
        });
        content.appendChild(stats);
        const descSec = document.createElement('div');
        descSec.className = 'card-section card-description';
        const h3 = document.createElement('h3');
        h3.textContent = '説明';
        const p = document.createElement('p');
        p.textContent = data.description;
        descSec.appendChild(h3);
        descSec.appendChild(p);
        content.appendChild(descSec);
        modalBody.appendChild(content);
        modal.classList.add('show');
        modal.focus();
    }

    function closeModal() { modal.classList.remove('show'); }
    modal.querySelector('.modal-close-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
    modal.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

    document.querySelectorAll('.monster-item').forEach(item => {
        item.addEventListener('click', () => {
            const data = JSON.parse(item.dataset.details);
            displayDetails(data);
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
                draggedItem.parentElement.appendChild(existing);
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
