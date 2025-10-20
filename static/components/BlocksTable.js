// static/pages/BlocksTable.js
import { h } from 'preact';
import { useEffect, useRef } from 'preact/hooks';
import { PAGE, API, TABLE_SIZE } from '../lib/api.js?dev=1';
import { streamNdjson, ensureFixedRowCount, shortenHex } from '../lib/utils.js?dev=1';

export default function BlocksTable() {
    const bodyRef = useRef(null);
    const countRef = useRef(null);
    const abortRef = useRef(null);
    const seenKeysRef = useRef(new Set());

    useEffect(() => {
        const body = bodyRef.current;
        const counter = countRef.current;

        // 5 columns now (ID, Slot, Root, Parent, Transactions)
        ensureFixedRowCount(body, 5, TABLE_SIZE);

        abortRef.current?.abort();
        abortRef.current = new AbortController();

        const pruneAndPad = () => {
            for (let i = body.rows.length - 1; i >= 0; i--) {
                if (body.rows[i].classList.contains('ph')) body.deleteRow(i);
            }
            while ([...body.rows].filter((r) => !r.classList.contains('ph')).length > TABLE_SIZE) {
                const last = body.rows[body.rows.length - 1];
                const key = last?.dataset?.key;
                if (key) seenKeysRef.current.delete(key);
                body.deleteRow(-1);
            }
            // keep placeholders in sync with 5 columns
            ensureFixedRowCount(body, 5, TABLE_SIZE);
            const real = [...body.rows].filter((r) => !r.classList.contains('ph')).length;
            counter.textContent = String(real);
        };

        const navigateToBlockDetail = (blockId) => {
            history.pushState({}, '', PAGE.BLOCK_DETAIL(blockId));
            window.dispatchEvent(new PopStateEvent('popstate'));
        };

        const appendRow = (b, key) => {
            const tr = document.createElement('tr');
            tr.dataset.key = key;

            // ID (clickable)
            const tdId = document.createElement('td');
            const linkId = document.createElement('a');
            linkId.className = 'linkish mono';
            linkId.href = PAGE.BLOCK_DETAIL(b.id);
            linkId.textContent = String(b.id);
            linkId.addEventListener('click', (e) => {
                e.preventDefault();
                navigateToBlockDetail(b.id);
            });
            tdId.appendChild(linkId);

            // Slot
            const tdSlot = document.createElement('td');
            const spSlot = document.createElement('span');
            spSlot.className = 'mono';
            spSlot.textContent = String(b.slot);
            tdSlot.appendChild(spSlot);

            // Root
            const tdRoot = document.createElement('td');
            const spRoot = document.createElement('span');
            spRoot.className = 'mono';
            spRoot.title = b.root;
            spRoot.textContent = shortenHex(b.root);
            tdRoot.appendChild(spRoot);

            // Parent
            const tdParent = document.createElement('td');
            const spParent = document.createElement('span');
            spParent.className = 'mono';
            spParent.title = b.parent;
            spParent.textContent = shortenHex(b.parent);
            tdParent.appendChild(spParent);

            // Transactions (array length)
            const tdCount = document.createElement('td');
            const spCount = document.createElement('span');
            spCount.className = 'mono';
            spCount.textContent = String(b.transactionCount);
            tdCount.appendChild(spCount);

            tr.append(tdId, tdSlot, tdRoot, tdParent, tdCount);
            body.insertBefore(tr, body.firstChild);
            pruneAndPad();
        };

        const normalize = (raw) => {
            const header = raw.header ?? raw;
            const txLen = Array.isArray(raw.transactions)
                ? raw.transactions.length
                : Array.isArray(raw.txs)
                  ? raw.txs.length
                  : 0;

            return {
                id: Number(raw.id ?? 0),
                slot: Number(header?.slot ?? raw.slot ?? 0),
                root: header?.block_root ?? raw.block_root ?? '',
                parent: header?.parent_block ?? raw.parent_block ?? '',
                transactionCount: txLen,
            };
        };

        streamNdjson(
            `${API.BLOCKS_STREAM}?prefetch-limit=${encodeURIComponent(TABLE_SIZE)}`,
            (raw) => {
                const b = normalize(raw);
                const key = `${b.id}:${b.slot}`;
                if (seenKeysRef.current.has(key)) {
                    pruneAndPad();
                    return;
                }
                seenKeysRef.current.add(key);
                appendRow(b, key);
            },
            {
                signal: abortRef.current.signal,
                onError: (e) => {
                    console.error('Blocks stream error:', e);
                },
            },
        );

        return () => abortRef.current?.abort();
    }, []);

    return h(
        'div',
        { class: 'card' },
        h(
            'div',
            { class: 'card-header' },
            h('div', null, h('strong', null, 'Blocks '), h('span', { class: 'pill', ref: countRef }, '0')),
            h('div', { style: 'color:var(--muted); fontSize:12px;' }),
        ),
        h(
            'div',
            { class: 'table-wrapper' },
            h(
                'table',
                { class: 'table--blocks' },
                h(
                    'colgroup',
                    null,
                    h('col', { style: 'width:80px' }), // ID
                    h('col', { style: 'width:90px' }), // Slot
                    h('col', { style: 'width:240px' }), // Root
                    h('col', { style: 'width:240px' }), // Parent
                    h('col', { style: 'width:120px' }), // Transactions
                ),
                h(
                    'thead',
                    null,
                    h(
                        'tr',
                        null,
                        h('th', null, 'ID'),
                        h('th', null, 'Slot'),
                        h('th', null, 'Block Root'),
                        h('th', null, 'Parent'),
                        h('th', null, 'Transactions'),
                    ),
                ),
                h('tbody', { ref: bodyRef }),
            ),
        ),
    );
}
