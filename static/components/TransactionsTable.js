import { h } from 'preact';
import { useEffect, useRef } from 'preact/hooks';
import { TRANSACTIONS_ENDPOINT, TABLE_SIZE } from '../lib/api.js?dev=1';
import {streamNdjson, ensureFixedRowCount, shortenHex, formatTimestamp, withBenignFilter} from '../lib/utils.js?dev=1';

export default function TransactionsTable() {
    const tbodyRef = useRef(null);
    const countRef = useRef(null);
    const abortRef = useRef(null);
    const totalCountRef = useRef(0);

    useEffect(() => {
        const tbody = tbodyRef.current;
        const counter = countRef.current;
        ensureFixedRowCount(tbody, 4, TABLE_SIZE);

        abortRef.current?.abort();
        abortRef.current = new AbortController();

        const makeSpan = (className, text, title) => {
            const s = document.createElement('span');
            if (className) s.className = className;
            if (title) s.title = title;
            s.textContent = text;
            return s;
        };
        const makeLink = (href, text, title) => {
            const a = document.createElement('a');
            a.className = 'linkish mono';
            a.href = href;
            if (title) a.title = title;
            a.textContent = text;
            return a;
        };

        const url = `${TRANSACTIONS_ENDPOINT}?prefetch-limit=${encodeURIComponent(TABLE_SIZE)}`;
        streamNdjson(
            url,
            (t) => {
                const row = document.createElement('tr');

                const cellHash = document.createElement('td');
                cellHash.appendChild(makeLink(`/transaction/${t.hash ?? ''}`, shortenHex(t.hash ?? ''), t.hash ?? ''));

                const cellFromTo = document.createElement('td');
                cellFromTo.appendChild(makeSpan('mono', shortenHex(t.sender ?? ''), t.sender ?? ''));
                cellFromTo.appendChild(document.createTextNode(' \u2192 '));
                cellFromTo.appendChild(makeSpan('mono', shortenHex(t.recipient ?? ''), t.recipient ?? ''));

                const cellAmount = document.createElement('td');
                cellAmount.className = 'amount';
                cellAmount.textContent = Number(t.amount ?? 0).toLocaleString(undefined, { maximumFractionDigits: 8 });

                const cellTime = document.createElement('td');
                const spanTime = makeSpan('mono', formatTimestamp(t.timestamp), t.timestamp ?? '');
                cellTime.appendChild(spanTime);

                row.append(cellHash, cellFromTo, cellAmount, cellTime);
                tbody.insertBefore(row, tbody.firstChild);
                while (tbody.rows.length > TABLE_SIZE) tbody.deleteRow(-1);
                counter.textContent = String(++totalCountRef.current);
            },
            {
                signal: abortRef.current.signal,
                onError: withBenignFilter(
                    (e) => console.error('Transaction stream error:', e),
                    abortRef.current.signal
                )
            },
        ).catch((err) => {
            if (!abortRef.current.signal.aborted) console.error('Transactions stream error:', err);
        });

        return () => abortRef.current?.abort();
    }, []);

    return h(
        'div',
        { class: 'card' },
        h(
            'div',
            { class: 'card-header' },
            h('div', null, h('strong', null, 'Transactions '), h('span', { class: 'pill', ref: countRef }, '0')),
            h('div', { style: 'color:var(--muted); font-size:12px;' }, '/api/v1/transactions/stream'),
        ),
        h(
            'div',
            { class: 'table-wrapper' },
            h(
                'table',
                { class: 'table--transactions' },
                h(
                    'colgroup',
                    null,
                    h('col', { style: 'width:260px' }),
                    h('col', null),
                    h('col', { style: 'width:120px' }),
                    h('col', { style: 'width:180px' }),
                ),
                h(
                    'thead',
                    null,
                    h('tr', null, h('th', null, 'Hash'), h('th', null, 'From → To'), h('th', null, 'Amount'), h('th', null, 'Time')),
                ),
                h('tbody', { ref: tbodyRef }),
            ),
        ),
    );
}
