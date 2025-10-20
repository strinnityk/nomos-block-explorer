import { h } from 'preact';
import { useEffect, useRef } from 'preact/hooks';
import { API, TABLE_SIZE } from '../lib/api.js?dev=1';
import {
    streamNdjson,
    ensureFixedRowCount,
    shortenHex,
    formatTimestamp,
    withBenignFilter,
} from '../lib/utils.js?dev=1';

const OPERATIONS_PREVIEW_LIMIT = 2;

function createSpan(className, text, title) {
    const element = document.createElement('span');
    if (className) element.className = className;
    if (title) element.title = title;
    element.textContent = text;
    return element;
}

function createLink(href, text, title) {
    const element = document.createElement('a');
    element.className = 'linkish mono';
    element.href = href;
    if (title) element.title = title;
    element.textContent = text;
    return element;
}

function normalizeTransaction(raw) {
    // Defensive parsing and intent-revealing structure
    const operations = Array.isArray(raw?.ops) ? raw.ops : Array.isArray(raw?.operations) ? raw.operations : [];

    const ledgerOutputs = Array.isArray(raw?.ledger_transaction?.outputs) ? raw.ledger_transaction.outputs : [];

    const totalOutputValue = ledgerOutputs.reduce((sum, note) => sum + Number(note?.value ?? 0), 0);

    return {
        id: raw?.id ?? '',
        operations,
        createdAt: raw?.created_at ?? raw?.timestamp ?? '',
        executionGasPrice: Number(raw?.execution_gas_price ?? 0),
        storageGasPrice: Number(raw?.storage_gas_price ?? 0),
        numberOfOutputs: ledgerOutputs.length,
        totalOutputValue,
    };
}

function formatOperationsPreview(operations) {
    if (operations.length === 0) return '—';
    if (operations.length <= OPERATIONS_PREVIEW_LIMIT) return operations.join(', ');
    const head = operations.slice(0, OPERATIONS_PREVIEW_LIMIT).join(', ');
    const remainder = operations.length - OPERATIONS_PREVIEW_LIMIT;
    return `${head} +${remainder}`;
}

function buildTransactionRow(transactionData) {
    const row = document.createElement('tr');

    // ID
    const cellId = document.createElement('td');
    cellId.className = 'mono';
    cellId.appendChild(
        createLink(`/transactions/${transactionData.id}`, String(transactionData.id), String(transactionData.id)),
    );

    // Operations
    const cellOperations = document.createElement('td');
    const operationsPreview = formatOperationsPreview(transactionData.operations);
    cellOperations.appendChild(createSpan('', operationsPreview, transactionData.operations.join(', ')));

    // Outputs (count / total value)
    const cellOutputs = document.createElement('td');
    cellOutputs.className = 'amount';
    cellOutputs.textContent = `${transactionData.numberOfOutputs} / ${transactionData.totalOutputValue.toLocaleString(undefined, { maximumFractionDigits: 8 })}`;

    // Gas (execution / storage)
    const cellGas = document.createElement('td');
    cellGas.className = 'mono';
    cellGas.textContent = `${transactionData.executionGasPrice.toLocaleString()} / ${transactionData.storageGasPrice.toLocaleString()}`;

    // Time
    const cellTime = document.createElement('td');
    const timeSpan = createSpan('mono', formatTimestamp(transactionData.createdAt), String(transactionData.createdAt));
    cellTime.appendChild(timeSpan);

    row.append(cellId, cellOperations, cellOutputs, cellGas, cellTime);
    return row;
}

export default function TransactionsTable() {
    const tableBodyRef = useRef(null);
    const counterRef = useRef(null);
    const abortControllerRef = useRef(null);
    const totalCountRef = useRef(0);

    useEffect(() => {
        const tableBodyElement = tableBodyRef.current;
        const counterElement = counterRef.current;
        ensureFixedRowCount(tableBodyElement, 4, TABLE_SIZE);

        abortControllerRef.current?.abort();
        abortControllerRef.current = new AbortController();

        const url = `${API.TRANSACTIONS_STREAM}?prefetch-limit=${encodeURIComponent(TABLE_SIZE)}`;

        streamNdjson(
            url,
            (rawTransaction) => {
                try {
                    const transactionData = normalizeTransaction(rawTransaction);
                    const row = buildTransactionRow(transactionData);

                    tableBodyElement.insertBefore(row, tableBodyElement.firstChild);
                    while (tableBodyElement.rows.length > TABLE_SIZE) tableBodyElement.deleteRow(-1);
                    counterElement.textContent = String(++totalCountRef.current);
                } catch (error) {
                    // Fail fast per row, but do not break the stream
                    console.error('Failed to render transaction row:', error);
                }
            },
            {
                signal: abortControllerRef.current.signal,
                onError: withBenignFilter(
                    (error) => console.error('Transaction stream error:', error),
                    abortControllerRef.current.signal,
                ),
            },
        ).catch((error) => {
            if (!abortControllerRef.current.signal.aborted) {
                console.error('Transactions stream connection error:', error);
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
            h('div', null, h('strong', null, 'Transactions '), h('span', { class: 'pill', ref: counterRef }, '0')),
            h('div', { style: 'color:var(--muted); font-size:12px;' }),
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
                    h('col', { style: 'width:120px' }), // ID
                    h('col', null), // Operations
                    h('col', { style: 'width:180px' }), // Outputs (count / total)
                    h('col', { style: 'width:180px' }), // Gas (execution / storage)
                    h('col', { style: 'width:180px' }), // Time
                ),
                h(
                    'thead',
                    null,
                    h(
                        'tr',
                        null,
                        h('th', null, 'ID'),
                        h('th', null, 'Operations'),
                        h('th', null, 'Outputs (count / total)'),
                        h('th', null, 'Gas (execution / storage)'),
                        h('th', null, 'Time'),
                    ),
                ),
                h('tbody', { ref: tableBodyRef }),
            ),
        ),
    );
}
