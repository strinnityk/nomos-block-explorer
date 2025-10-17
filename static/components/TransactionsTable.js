import { h } from 'preact';
import { useEffect, useRef } from 'preact/hooks';
import { TRANSACTIONS_ENDPOINT, TABLE_SIZE } from '../lib/api.js?dev=1';
import { streamNdjson, ensureFixedRowCount, shortenHex, formatTimestamp } from '../lib/utils.js?dev=1';

export default function TransactionsTable() {
    const tableBodyRef = useRef(null);
    const totalCountPillRef = useRef(null);
    const abortControllerRef = useRef(null);
    const totalStreamedCountRef = useRef(0);

    useEffect(() => {
        const tableBody = tableBodyRef.current;
        const totalCountPill = totalCountPillRef.current;
        const PLACEHOLDER_CLASS = 'ph';

        ensureFixedRowCount(tableBody, 4, TABLE_SIZE);

        abortControllerRef.current?.abort();
        abortControllerRef.current = new AbortController();

        const createSpan = (className, textContent, title) => {
            const element = document.createElement('span');
            if (className) element.className = className;
            if (title) element.title = title;
            element.textContent = textContent;
            return element;
        };

        const createLink = (href, textContent, title) => {
            const element = document.createElement('a');
            element.className = 'linkish mono';
            element.href = href;
            if (title) element.title = title;
            element.textContent = textContent;
            return element;
        };

        const countNonPlaceholderRows = () =>
            [...tableBody.rows].filter((row) => !row.classList.contains(PLACEHOLDER_CLASS)).length;

        const appendTransactionRow = (transaction) => {
            // Trim one placeholder from the end to keep height stable
            const lastRow = tableBody.rows[tableBody.rows.length - 1];
            if (lastRow?.classList.contains(PLACEHOLDER_CLASS)) tableBody.deleteRow(-1);

            const row = document.createElement('tr');

            const cellHash = document.createElement('td');
            cellHash.appendChild(
                createLink(
                    `/transaction/${transaction.hash ?? ''}`,
                    shortenHex(transaction.hash ?? ''),
                    transaction.hash ?? '',
                ),
            );

            const cellSenderRecipient = document.createElement('td');
            cellSenderRecipient.appendChild(
                createSpan('mono', shortenHex(transaction.sender ?? ''), transaction.sender ?? ''),
            );
            cellSenderRecipient.appendChild(document.createTextNode(' \u2192 '));
            cellSenderRecipient.appendChild(
                createSpan('mono', shortenHex(transaction.recipient ?? ''), transaction.recipient ?? ''),
            );

            const cellAmount = document.createElement('td');
            cellAmount.className = 'amount';
            const amount = Number(transaction.amount ?? 0);
            cellAmount.textContent = Number.isFinite(amount)
                ? amount.toLocaleString(undefined, { maximumFractionDigits: 8 })
                : '—';

            const cellTime = document.createElement('td');
            cellTime.appendChild(
                createSpan('mono', formatTimestamp(transaction.timestamp), transaction.timestamp ?? ''),
            );

            row.append(cellHash, cellSenderRecipient, cellAmount, cellTime);
            tableBody.insertBefore(row, tableBody.firstChild);

            // Trim to TABLE_SIZE (counting only non-placeholder rows)
            while (countNonPlaceholderRows() > TABLE_SIZE) tableBody.deleteRow(-1);

            totalCountPill.textContent = String(++totalStreamedCountRef.current);
        };

        streamNdjson(TRANSACTIONS_ENDPOINT, (transaction) => appendTransactionRow(transaction), {
            signal: abortControllerRef.current.signal,
        }).catch((error) => {
            if (!abortControllerRef.current.signal.aborted) {
                console.error('Transactions stream error:', error);
            }
        });

        return () => abortControllerRef.current?.abort();
    }, []);

    return h(
        'div',
        { class: 'card' },
        h(
            'div',
            { class: 'card-header' },
            h(
                'div',
                null,
                h('strong', null, 'Transactions '),
                h('span', { class: 'pill', ref: totalCountPillRef }, '0'),
            ),
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
                    h(
                        'tr',
                        null,
                        h('th', null, 'Hash'),
                        h('th', null, 'From → To'),
                        h('th', null, 'Amount'),
                        h('th', null, 'Time'),
                    ),
                ),
                h('tbody', { ref: tableBodyRef }),
            ),
        ),
    );
}
