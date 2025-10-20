// static/pages/TransactionDetail.js
import { h, Fragment } from 'preact';
import { useEffect, useMemo, useState } from 'preact/hooks';
import { API } from '../lib/api.js?dev=1';

// ————— helpers —————
const isNumber = (v) => typeof v === 'number' && !Number.isNaN(v);
const toLocaleNum = (n, opts = {}) => Number(n ?? 0).toLocaleString(undefined, { maximumFractionDigits: 8, ...opts });

// Try to render bytes in a readable way without guessing too hard
function renderBytes(value) {
    if (typeof value === 'string') return value; // hex/base64/etc.
    if (Array.isArray(value) && value.every((x) => Number.isInteger(x) && x >= 0 && x <= 255)) {
        return '0x' + value.map((b) => b.toString(16).padStart(2, '0')).join('');
    }
    try {
        return JSON.stringify(value);
    } catch {
        return String(value);
    }
}

// ————— normalizer (robust to partial data) —————
function normalizeTransaction(raw) {
    const ops = Array.isArray(raw?.operations) ? raw.operations : [];
    const lt = raw?.ledger_transaction ?? {};
    const inputs = Array.isArray(lt?.inputs) ? lt.inputs : [];
    const outputs = Array.isArray(lt?.outputs) ? lt.outputs : [];

    const totalOutputValue = outputs.reduce((sum, note) => sum + Number(note?.value ?? 0), 0);

    return {
        id: raw?.id ?? '',
        blockId: raw?.block_id ?? null,
        operations: ops.map(String),
        executionGasPrice: isNumber(raw?.execution_gas_price)
            ? raw.execution_gas_price
            : Number(raw?.execution_gas_price ?? 0),
        storageGasPrice: isNumber(raw?.storage_gas_price) ? raw.storage_gas_price : Number(raw?.storage_gas_price ?? 0),
        ledger: { inputs, outputs, totalOutputValue },
    };
}

// ————— UI bits —————
function SectionCard({ title, children, style }) {
    return h(
        'div',
        { class: 'card', style: `margin-top:12px; ${style ?? ''}` },
        h('div', { class: 'card-header' }, h('strong', null, title)),
        h('div', { style: 'padding:12px 14px' }, children),
    );
}

function Summary({ tx }) {
    return h(
        SectionCard,
        { title: 'Summary' },
        h(
            'div',
            { style: 'display:grid; gap:8px;' },

            // (ID removed)

            tx.blockId != null &&
                h(
                    'div',
                    null,
                    h('b', null, 'Block: '),
                    h(
                        'a',
                        { class: 'linkish mono', href: API.BLOCK_DETAIL_BY_ID(tx.blockId), title: String(tx.blockId) },
                        String(tx.blockId),
                    ),
                ),

            h(
                'div',
                null,
                h('b', null, 'Execution Gas: '),
                h('span', { class: 'mono' }, toLocaleNum(tx.executionGasPrice)),
            ),
            h(
                'div',
                null,
                h('b', null, 'Storage Gas: '),
                h('span', { class: 'mono' }, toLocaleNum(tx.storageGasPrice)),
            ),

            h(
                'div',
                null,
                h('b', null, 'Operations: '),
                tx.operations?.length
                    ? h(
                          'span',
                          { style: 'display:inline-flex; gap:6px; flex-wrap:wrap; vertical-align:middle;' },
                          ...tx.operations.map((op, i) => h('span', { key: i, class: 'pill', title: op }, op)),
                      )
                    : h('span', { style: 'color:var(--muted)' }, '—'),
            ),
        ),
    );
}

function InputsTable({ inputs }) {
    if (!inputs?.length) {
        return h('div', { style: 'color:var(--muted)' }, '—');
    }

    return h(
        'div',
        { class: 'table-wrapper', style: 'margin-top:6px;' },
        h(
            'table',
            { class: 'table--transactions' },
            h(
                'colgroup',
                null,
                h('col', { style: 'width:80px' }), // #
                h('col', null), // Value (fills)
            ),
            h('thead', null, h('tr', null, h('th', { style: 'text-align:center;' }, '#'), h('th', null, 'Value'))),
            h(
                'tbody',
                null,
                ...inputs.map((fr, i) =>
                    h(
                        'tr',
                        { key: i },
                        h('td', { style: 'text-align:center;' }, String(i)),
                        h(
                            'td',
                            null,
                            h(
                                'span',
                                { class: 'mono', style: 'overflow-wrap:anywhere; word-break:break-word;' },
                                String(fr),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    );
}

function OutputsTable({ outputs }) {
    if (!outputs?.length) {
        return h('div', { style: 'color:var(--muted)' }, '—');
    }

    return h(
        'div',
        { class: 'table-wrapper', style: 'margin-top:6px;' },
        h(
            'table',
            { class: 'table--transactions' },
            h(
                'colgroup',
                null,
                h('col', { style: 'width:80px' }), // # (compact, centered)
                h('col', null), // Public Key (fills)
                h('col', { style: 'width:180px' }), // Value (compact, right)
            ),
            h(
                'thead',
                null,
                h(
                    'tr',
                    null,
                    h('th', { style: 'text-align:center;' }, '#'),
                    h('th', null, 'Public Key'), // ← back to Public Key second
                    h('th', { style: 'text-align:right;' }, 'Value'), // ← Value last
                ),
            ),
            h(
                'tbody',
                null,
                ...outputs.map((note, idx) =>
                    h(
                        'tr',
                        { key: idx },
                        // # (index)
                        h('td', { style: 'text-align:center;' }, String(idx)),

                        // Public Key (fills, wraps)
                        h(
                            'td',
                            null,
                            h(
                                'span',
                                {
                                    class: 'mono',
                                    style: 'display:inline-block; overflow-wrap:anywhere; word-break:break-word;',
                                    title: renderBytes(note?.public_key),
                                },
                                renderBytes(note?.public_key),
                            ),
                        ),

                        // Value (right-aligned)
                        h('td', { class: 'amount', style: 'text-align:right;' }, toLocaleNum(note?.value)),
                    ),
                ),
            ),
        ),
    );
}

function Ledger({ ledger }) {
    const { inputs, outputs, totalOutputValue } = ledger;

    // Sum inputs as integers (Fr is declared as int in your schema)
    const totalInputValue = inputs.reduce((sum, v) => sum + Number(v ?? 0), 0);

    return h(
        SectionCard,
        { title: 'Ledger Transaction' },
        h(
            'div',
            { style: 'display:grid; gap:16px;' },

            // Inputs (with Total on the right)
            h(
                'div',
                null,
                h(
                    'div',
                    { style: 'display:flex; align-items:center; gap:8px;' },
                    h('b', null, 'Inputs'),
                    h('span', { class: 'pill' }, String(inputs.length)),
                    h(
                        'span',
                        { class: 'amount', style: 'margin-left:auto;' },
                        `Total: ${toLocaleNum(totalInputValue)}`,
                    ),
                ),
                h(InputsTable, { inputs }),
            ),

            // Outputs (unchanged header total)
            h(
                'div',
                null,
                h(
                    'div',
                    { style: 'display:flex; align-items:center; gap:8px;' },
                    h('b', null, 'Outputs'),
                    h('span', { class: 'pill' }, String(outputs.length)),
                    h(
                        'span',
                        { class: 'amount', style: 'margin-left:auto;' },
                        `Total: ${toLocaleNum(totalOutputValue)}`,
                    ),
                ),
                h(OutputsTable, { outputs }),
            ),
        ),
    );
}

// ————— page —————
export default function TransactionDetail({ parameters }) {
    const idParam = parameters?.[0];
    const id = Number.parseInt(String(idParam), 10);
    const isValidId = Number.isInteger(id) && id >= 0;

    const [tx, setTx] = useState(null);
    const [err, setErr] = useState(null); // { kind: 'invalid'|'not-found'|'network', msg: string }

    const pageTitle = useMemo(() => `Transaction ${String(idParam)}`, [idParam]);
    useEffect(() => {
        document.title = pageTitle;
    }, [pageTitle]);

    useEffect(() => {
        setTx(null);
        setErr(null);

        if (!isValidId) {
            setErr({ kind: 'invalid', msg: 'Invalid transaction id.' });
            return;
        }

        let alive = true;
        const controller = new AbortController();

        (async () => {
            try {
                const res = await fetch(API.TRANSACTION_DETAIL_BY_ID(id), {
                    cache: 'no-cache',
                    signal: controller.signal,
                });
                if (res.status === 404 || res.status === 410) {
                    if (alive) setErr({ kind: 'not-found', msg: 'Transaction not found.' });
                    return;
                }
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const payload = await res.json();
                if (!alive) return;
                setTx(normalizeTransaction(payload));
            } catch (e) {
                if (!alive || e?.name === 'AbortError') return;
                setErr({ kind: 'network', msg: e?.message ?? 'Failed to load transaction' });
            }
        })();

        return () => {
            alive = false;
            controller.abort();
        };
    }, [id, isValidId]);

    return h(
        'main',
        { class: 'wrap' },

        h(
            'header',
            { style: 'display:flex; gap:12px; align-items:center; margin:12px 0;' },
            h('a', { class: 'linkish', href: '/' }, '← Back'),
            h('h1', { style: 'margin:0' }, pageTitle),
        ),

        // Errors
        err?.kind === 'invalid' && h('p', { style: 'color:#ff8a8a' }, err.msg),
        err?.kind === 'not-found' &&
            h(
                SectionCard,
                { title: 'Transaction not found' },
                h('p', null, 'We could not find a transaction with that identifier.'),
            ),
        err?.kind === 'network' && h('p', { style: 'color:#ff8a8a' }, `Error: ${err.msg}`),

        // Loading
        !tx && !err && h('p', null, 'Loading…'),

        // Success
        tx && h(Fragment, null, h(Summary, { tx }), h(Ledger, { ledger: tx.ledger })),
    );
}
