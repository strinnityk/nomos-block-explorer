import { h } from 'preact';
import { useEffect, useRef } from 'preact/hooks';
import { BLOCKS_ENDPOINT, TABLE_SIZE } from '../lib/api.js?dev=1';
import {streamNdjson, ensureFixedRowCount, shortenHex, formatTimestamp, withBenignFilter} from '../lib/utils.js?dev=1';

export default function BlocksTable() {
    const tbodyRef = useRef(null);
    const countRef = useRef(null);
    const abortRef = useRef(null);
    const seenKeysRef = useRef(new Set());

    useEffect(() => {
        const tbody = tbodyRef.current;
        const counter = countRef.current;
        ensureFixedRowCount(tbody, 5, TABLE_SIZE);

        abortRef.current?.abort();
        abortRef.current = new AbortController();

        function pruneAndPad() {
            // remove placeholders
            for (let i = tbody.rows.length - 1; i >= 0; i--) {
                if (tbody.rows[i].classList.contains('ph')) tbody.deleteRow(i);
            }
            // trim overflow
            while ([...tbody.rows].filter((r) => !r.classList.contains('ph')).length > TABLE_SIZE) {
                const last = tbody.rows[tbody.rows.length - 1];
                const key = last?.dataset?.key;
                if (key) seenKeysRef.current.delete(key);
                tbody.deleteRow(-1);
            }
            // pad placeholders
            const real = [...tbody.rows].filter((r) => !r.classList.contains('ph')).length;
            ensureFixedRowCount(tbody, 5, TABLE_SIZE);
            counter.textContent = String(real);
        }

        const makeLink = (href, text, title) => {
            const a = document.createElement('a');
            a.className = 'linkish mono';
            a.href = href;
            if (title) a.title = title;
            a.textContent = text;
            return a;
        };

        const appendRow = (block, key) => {
            const row = document.createElement('tr');
            row.dataset.key = key;

            const cellSlot = document.createElement('td');
            const spanSlot = document.createElement('span');
            spanSlot.className = 'mono';
            spanSlot.textContent = String(block.slot);
            cellSlot.appendChild(spanSlot);

            const cellRoot = document.createElement('td');
            cellRoot.appendChild(makeLink(`/block/${block.root}`, shortenHex(block.root), block.root));

            const cellParent = document.createElement('td');
            cellParent.appendChild(makeLink(`/block/${block.parent}`, shortenHex(block.parent), block.parent));

            const cellTxCount = document.createElement('td');
            const spanTx = document.createElement('span');
            spanTx.className = 'mono';
            spanTx.textContent = String(block.transactionCount);
            cellTxCount.appendChild(spanTx);

            const cellTime = document.createElement('td');
            const spanTime = document.createElement('span');
            spanTime.className = 'mono';
            spanTime.title = block.time ?? '';
            spanTime.textContent = formatTimestamp(block.time);
            cellTime.appendChild(spanTime);

            row.append(cellSlot, cellRoot, cellParent, cellTxCount, cellTime);
            tbody.insertBefore(row, tbody.firstChild);
            pruneAndPad();
        };

        const normalize = (raw) => {
            const header = raw.header ?? raw;
            const created = raw.created_at ?? raw.header?.created_at ?? null;
            return {
                id: Number(raw.id ?? 0),
                slot: Number(header?.slot ?? raw.slot ?? 0),
                root: header?.block_root ?? raw.block_root ?? '',
                parent: header?.parent_block ?? raw.parent_block ?? '',
                transactionCount: Array.isArray(raw.transactions)
                    ? raw.transactions.length
                    : typeof raw.transaction_count === 'number'
                        ? raw.transaction_count
                        : 0,
                time: created,
            };
        };

        const url = `${BLOCKS_ENDPOINT}?prefetch-limit=${encodeURIComponent(TABLE_SIZE)}`;
        streamNdjson(
            url,
            (raw) => {
                const block = normalize(raw);
                const key = `${block.slot}:${block.id}`;
                if (seenKeysRef.current.has(key)) {
                    pruneAndPad();
                    return;
                }
                seenKeysRef.current.add(key);
                appendRow(block, key);
            },
            {
                signal: abortRef.current.signal,
                onError: withBenignFilter(
                    (e) => console.error('Blocks stream error:', e),
                    abortRef.current.signal
                )
            },
        ).catch((err) => {
            if (!abortRef.current.signal.aborted) console.error('Blocks stream error:', err);
        });

        return () => abortRef.current?.abort();
    }, []);

    return h(
        'div',
        { class: 'card' },
        h(
            'div',
            { class: 'card-header' },
            h('div', null, h('strong', null, 'Blocks '), h('span', { class: 'pill', ref: countRef }, '0')),
            h('div', { style: 'color:var(--muted); font-size:12px;' }, '/api/v1/blocks/stream'),
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
                    h('col', { style: 'width:90px' }),
                    h('col', { style: 'width:260px' }),
                    h('col', { style: 'width:260px' }),
                    h('col', { style: 'width:120px' }),
                    h('col', { style: 'width:180px' }),
                ),
                h(
                    'thead',
                    null,
                    h('tr', null, h('th', null, 'Slot'), h('th', null, 'Block Root'), h('th', null, 'Parent'), h('th', null, 'Transactions'), h('th', null, 'Time')),
                ),
                h('tbody', { ref: tbodyRef }),
            ),
        ),
    );
}
