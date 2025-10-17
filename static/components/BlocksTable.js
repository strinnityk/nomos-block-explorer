import { h } from 'preact';
import { useEffect, useRef } from 'preact/hooks';
import { BLOCKS_ENDPOINT, TABLE_SIZE } from '../lib/api.js';
import { streamNdjson, ensureFixedRowCount, shortenHex, formatTimestamp } from '../lib/utils.js';

const COLUMN_COUNT = 5;

export default function BlocksTable() {
    const tbodyRef = useRef(null);
    const counterRef = useRef(null);
    const controllerRef = useRef(null);
    const seenKeysRef = useRef(new Set());

    useEffect(() => {
        const tbody = tbodyRef.current;
        const counter = counterRef.current;

        ensureFixedRowCount(tbody, COLUMN_COUNT, TABLE_SIZE);

        controllerRef.current?.abort();
        controllerRef.current = new AbortController();

        function updateCounter() {
            let realRows = 0;
            for (const row of tbody.rows) {
                if (!row.classList.contains('ph')) realRows++;
            }
            counter.textContent = String(realRows);
        }

        function removePlaceholders() {
            for (let i = tbody.rows.length - 1; i >= 0; i--) {
                if (tbody.rows[i].classList.contains('ph')) tbody.deleteRow(i);
            }
        }

        function trimToTableSize() {
            // count real rows
            let realRows = 0;
            for (const row of tbody.rows) {
                if (!row.classList.contains('ph')) realRows++;
            }
            // drop rows beyond limit, and forget their keys
            while (realRows > TABLE_SIZE) {
                const last = tbody.rows[tbody.rows.length - 1];
                const key = last?.dataset?.key;
                if (key) seenKeysRef.current.delete(key);
                tbody.deleteRow(-1);
                realRows--;
            }
        }

        function makeLink(href, text, title) {
            const anchor = document.createElement('a');
            anchor.className = 'linkish mono';
            anchor.href = href;
            if (title) anchor.title = title;
            anchor.textContent = text;
            return anchor;
        }

        function appendRow(block, key) {
            const row = document.createElement('tr');
            row.dataset.key = key;

            const slotCell = document.createElement('td');
            const slotSpan = document.createElement('span');
            slotSpan.className = 'mono';
            slotSpan.textContent = String(block.slot);
            slotCell.appendChild(slotSpan);

            const rootCell = document.createElement('td');
            rootCell.appendChild(makeLink(`/block/${block.root}`, shortenHex(block.root), block.root));

            const parentCell = document.createElement('td');
            parentCell.appendChild(makeLink(`/block/${block.parent}`, shortenHex(block.parent), block.parent));

            const countCell = document.createElement('td');
            const countSpan = document.createElement('span');
            countSpan.className = 'mono';
            countSpan.textContent = String(block.transactionCount);
            countCell.appendChild(countSpan);

            const timeCell = document.createElement('td');
            const timeSpan = document.createElement('span');
            timeSpan.className = 'mono';
            timeSpan.title = block.time ?? '';
            timeSpan.textContent = formatTimestamp(block.time);
            timeCell.appendChild(timeSpan);

            row.append(slotCell, rootCell, parentCell, countCell, timeCell);
            tbody.insertBefore(row, tbody.firstChild);

            // housekeeping
            removePlaceholders();
            trimToTableSize();
            ensureFixedRowCount(tbody, COLUMN_COUNT, TABLE_SIZE);
            updateCounter();
        }

        function normalizeBlock(raw) {
            const header = raw.header ?? raw;
            const createdAt = raw.created_at ?? raw.header?.created_at ?? null;
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
                time: createdAt,
            };
        }

        streamNdjson(
            BLOCKS_ENDPOINT,
            (raw) => {
                const block = normalizeBlock(raw);
                const key = `${block.slot}:${block.id}`;
                if (seenKeysRef.current.has(key)) {
                    // still keep placeholders consistent and counter fresh
                    removePlaceholders();
                    trimToTableSize();
                    ensureFixedRowCount(tbody, COLUMN_COUNT, TABLE_SIZE);
                    updateCounter();
                    return;
                }
                seenKeysRef.current.add(key);
                appendRow(block, key);
            },
            {
                signal: controllerRef.current.signal,
                onError: (err) => {
                    if (!controllerRef.current.signal.aborted) {
                        console.error('Blocks stream error:', err);
                    }
                },
            },
        );

        return () => controllerRef.current?.abort();
    }, []);

    return h(
        'div',
        { class: 'card' },
        h(
            'div',
            { class: 'card-header' },
            h('div', null, h('strong', null, 'Blocks '), h('span', { class: 'pill', ref: counterRef }, '0')),
            h('div', { style: 'color:var(--muted); font-size:12px;' }, BLOCKS_ENDPOINT),
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
                    h(
                        'tr',
                        null,
                        h('th', null, 'Slot'),
                        h('th', null, 'Block Root'),
                        h('th', null, 'Parent'),
                        h('th', null, 'Transactions'),
                        h('th', null, 'Time'),
                    ),
                ),
                h('tbody', { ref: tbodyRef }),
            ),
        ),
    );
}
