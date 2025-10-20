// static/pages/BlockDetailPage.js
import { h, Fragment } from 'preact';
import { useEffect, useMemo, useState } from 'preact/hooks';
import { API, PAGE } from '../lib/api.js?dev=1';

const OPERATIONS_PREVIEW_LIMIT = 2;

// Helpers
function opsToPills(ops, limit = OPERATIONS_PREVIEW_LIMIT) {
    const arr = Array.isArray(ops) ? ops : [];
    if (!arr.length) return h('span', { style: 'color:var(--muted); white-space:nowrap;' }, '—');
    const shown = arr.slice(0, limit);
    const extra = arr.length - shown.length;
    return h(
        'div',
        { style: 'display:flex; gap:6px; flex-wrap:nowrap; align-items:center; white-space:nowrap;' },
        ...shown.map((op, i) =>
            h('span', { key: `${op}-${i}`, class: 'pill', title: op, style: 'flex:0 0 auto;' }, op),
        ),
        extra > 0 && h('span', { class: 'pill', title: `${extra} more`, style: 'flex:0 0 auto;' }, `+${extra}`),
    );
}

function computeOutputsSummary(ledgerTransaction) {
    const outputs = Array.isArray(ledgerTransaction?.outputs) ? ledgerTransaction.outputs : [];
    const count = outputs.length;
    const total = outputs.reduce((sum, o) => sum + Number(o?.value ?? 0), 0);
    return { count, total };
}

function CopyPill({ text }) {
    const onCopy = async (e) => {
        e.preventDefault();
        try {
            await navigator.clipboard.writeText(String(text ?? ''));
        } catch {}
    };
    return h(
        'a',
        {
            class: 'pill linkish mono',
            style: 'cursor:pointer; user-select:none;',
            href: '#',
            onClick: onCopy,
            onKeyDown: (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onCopy(e);
                }
            },
            tabIndex: 0,
            role: 'button',
        },
        'Copy',
    );
}

export default function BlockDetailPage({ parameters }) {
    const blockIdParameter = parameters[0];
    const blockId = Number.parseInt(String(blockIdParameter), 10);
    const isValidId = Number.isInteger(blockId) && blockId >= 0;

    const [block, setBlock] = useState(null);
    const [errorMessage, setErrorMessage] = useState('');
    const [errorKind, setErrorKind] = useState(null); // 'invalid-id' | 'not-found' | 'network' | null

    const pageTitle = useMemo(() => `Block ${String(blockIdParameter)}`, [blockIdParameter]);
    useEffect(() => {
        document.title = pageTitle;
    }, [pageTitle]);

    useEffect(() => {
        setBlock(null);
        setErrorMessage('');
        setErrorKind(null);

        if (!isValidId) {
            setErrorKind('invalid-id');
            setErrorMessage('Invalid block id.');
            return;
        }

        let alive = true;
        const controller = new AbortController();

        (async () => {
            try {
                const res = await fetch(API.BLOCK_DETAIL_BY_ID(blockId), {
                    cache: 'no-cache',
                    signal: controller.signal,
                });
                if (res.status === 404 || res.status === 410) {
                    if (alive) {
                        setErrorKind('not-found');
                        setErrorMessage('Block not found.');
                    }
                    return;
                }
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const payload = await res.json();
                if (alive) setBlock(payload);
            } catch (e) {
                if (!alive || e?.name === 'AbortError') return;
                setErrorKind('network');
                setErrorMessage(e?.message ?? 'Failed to load block');
            }
        })();

        return () => {
            alive = false;
            controller.abort();
        };
    }, [blockId, isValidId]);

    const header = block?.header ?? {};
    const transactions = Array.isArray(block?.transactions) ? block.transactions : [];
    const slot = block?.slot ?? header.slot;

    return h(
        'main',
        { class: 'wrap' },

        // Top bar
        h(
            'header',
            { style: 'display:flex; gap:12px; align-items:center; margin:12px 0;' },
            h('a', { class: 'linkish', href: '/' }, '← Back'),
            h('h1', { style: 'margin:0' }, pageTitle),
        ),

        // Error states
        errorKind === 'invalid-id' && h('p', { style: 'color:#ff8a8a' }, errorMessage),
        errorKind === 'not-found' &&
            h(
                'div',
                { class: 'card', style: 'margin-top:12px;' },
                h('div', { class: 'card-header' }, h('strong', null, 'Block not found')),
                h(
                    'div',
                    { style: 'padding:12px 14px' },
                    h('p', null, 'We could not find a block with that identifier.'),
                ),
            ),
        errorKind === 'network' && h('p', { style: 'color:#ff8a8a' }, `Error: ${errorMessage}`),

        // Loading
        !block && !errorKind && h('p', null, 'Loading…'),

        // Success
        block &&
            h(
                Fragment,
                null,

                // Header card
                h(
                    'div',
                    { class: 'card', style: 'margin-top:12px;' },
                    h(
                        'div',
                        { class: 'card-header', style: 'display:flex; align-items:center; gap:8px;' },
                        h('strong', null, 'Header'),
                        h(
                            'div',
                            { style: 'margin-left:auto; display:flex; gap:8px; flex-wrap:wrap;' },
                            slot != null && h('span', { class: 'pill', title: 'Slot' }, `Slot ${String(slot)}`),
                        ),
                    ),
                    h(
                        'div',
                        { style: 'padding:12px 14px; display:grid; grid-template-columns: 120px 1fr; gap:8px 12px;' },

                        // Root (pill + copy)
                        h('div', null, h('b', null, 'Root:')),
                        h(
                            'div',
                            { style: 'display:flex; gap:8px; flex-wrap:wrap; align-items:flex-start;' },
                            h(
                                'span',
                                {
                                    class: 'pill mono',
                                    title: header.block_root ?? '',
                                    style: 'max-width:100%; overflow-wrap:anywhere; word-break:break-word;',
                                },
                                String(header.block_root ?? ''),
                            ),
                            h(CopyPill, { text: header.block_root }),
                        ),

                        // Parent (pill + copy)
                        h('div', null, h('b', null, 'Parent:')),
                        h(
                            'div',
                            { style: 'display:flex; gap:8px; flex-wrap:wrap; align-items:flex-start;' },
                            block?.parent_id
                                ? h(
                                      'a',
                                      {
                                          class: 'pill mono linkish',
                                          href: PAGE.BLOCK_DETAIL(block.parent_id),
                                          title: String(block.parent_id),
                                          style: 'max-width:100%; overflow-wrap:anywhere; word-break:break-word;',
                                      },
                                      String(block.parent_id),
                                  )
                                : h(
                                      'span',
                                      {
                                          class: 'pill mono',
                                          title: header.parent_block ?? '',
                                          style: 'max-width:100%; overflow-wrap:anywhere; word-break:break-word;',
                                      },
                                      String(header.parent_block ?? ''),
                                  ),
                            h(CopyPill, { text: block?.parent_id ?? header.parent_block }),
                        ),
                    ),
                ),

                // Transactions card — rows fill width; Outputs & Gas centered
                h(
                    'div',
                    { class: 'card', style: 'margin-top:16px;' },
                    h(
                        'div',
                        { class: 'card-header' },
                        h('strong', null, 'Transactions '),
                        h('span', { class: 'pill' }, String(transactions.length)),
                    ),
                    h(
                        'div',
                        { class: 'table-wrapper', style: 'max-width:100%; overflow:auto;' },
                        h(
                            'table',
                            {
                                class: 'table--transactions',
                                // Fill card by default; expand + scroll if content is wider
                                style: 'min-width:100%; width:max-content; table-layout:auto; border-collapse:collapse;',
                            },
                            h(
                                'thead',
                                null,
                                h(
                                    'tr',
                                    null,
                                    h('th', { style: 'text-align:left; padding:8px 10px; white-space:nowrap;' }, 'ID'),
                                    h(
                                        'th',
                                        { style: 'text-align:center; padding:8px 10px; white-space:nowrap;' },
                                        'Outputs (count / total)',
                                    ),
                                    h(
                                        'th',
                                        { style: 'text-align:center; padding:8px 10px; white-space:nowrap;' },
                                        'Gas (execution / storage)',
                                    ),
                                    h(
                                        'th',
                                        { style: 'text-align:left; padding:8px 10px; white-space:nowrap;' },
                                        'Operations',
                                    ),
                                ),
                            ),
                            h(
                                'tbody',
                                null,
                                ...transactions.map((t) => {
                                    const operations = Array.isArray(t?.operations) ? t.operations : [];
                                    const { count, total } = computeOutputsSummary(t?.ledger_transaction);
                                    const executionGas = Number(t?.execution_gas_price ?? 0);
                                    const storageGas = Number(t?.storage_gas_price ?? 0);

                                    return h(
                                        'tr',
                                        { key: t?.id ?? `${count}/${total}` },
                                        // ID (left)
                                        h(
                                            'td',
                                            { style: 'text-align:left; padding:8px 10px; white-space:nowrap;' },
                                            h(
                                                'a',
                                                {
                                                    class: 'linkish mono',
                                                    href: PAGE.TRANSACTION_DETAIL(t?.id ?? ''),
                                                    title: String(t?.id ?? ''),
                                                },
                                                String(t?.id ?? ''),
                                            ),
                                        ),
                                        // Outputs (center)
                                        h(
                                            'td',
                                            {
                                                class: 'amount',
                                                style: 'text-align:center; padding:8px 10px; white-space:nowrap;',
                                            },
                                            `${count} / ${Number(total).toLocaleString(undefined, { maximumFractionDigits: 8 })}`,
                                        ),
                                        // Gas (center)
                                        h(
                                            'td',
                                            {
                                                class: 'mono',
                                                style: 'text-align:center; padding:8px 10px; white-space:nowrap;',
                                            },
                                            `${executionGas.toLocaleString()} / ${storageGas.toLocaleString()}`,
                                        ),
                                        // Operations (left; no wrap)
                                        h(
                                            'td',
                                            { style: 'text-align:left; padding:8px 10px; white-space:nowrap;' },
                                            opsToPills(operations),
                                        ),
                                    );
                                }),
                            ),
                        ),
                    ),
                ),
            ),
    );
}
