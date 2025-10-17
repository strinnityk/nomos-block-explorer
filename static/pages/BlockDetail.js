import { h, Fragment } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import { shortenHex, formatTimestamp } from '../lib/utils.js?dev=1';
import { BLOCK_DETAIL } from '../lib/api.js?dev=1';

export default function BlockDetail({ params: routeParams }) {
    const blockId = routeParams[0];

    const [block, setBlock] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const controller = new AbortController();

        (async () => {
            try {
                const res = await fetch(BLOCK_DETAIL(blockId), {
                    signal: controller.signal,
                    cache: 'no-cache',
                });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                setBlock(data);
            } catch (err) {
                if (!controller.signal.aborted) setError(err.message || 'Request failed');
            }
        })();

        return () => controller.abort();
    }, [blockId]);

    const header = block?.header ?? {};
    const transactions = block?.transactions ?? [];

    return h(
        'main',
        { class: 'wrap' },
        h(
            'header',
            { style: 'display:flex; gap:12px; align-items:center; margin:12px 0;' },
            h('a', { class: 'linkish', href: '/' }, '← Back'),
            h('h1', { style: 'margin:0' }, `Block ${shortenHex(blockId, 12, 12)}`),
        ),

        error && h('p', { style: 'color:#ff8a8a' }, `Error: ${error}`),
        !block && !error && h('p', null, 'Loading…'),

        block &&
            h(
                Fragment,
                null,

                // Header card
                h(
                    'div',
                    { class: 'card', style: 'margin-top:12px;' },
                    h('div', { class: 'card-header' }, h('strong', null, 'Header')),
                    h(
                        'div',
                        { style: 'padding:12px 14px' },
                        h('div', null, h('b', null, 'Slot: '), h('span', { class: 'mono' }, header.slot ?? '')),
                        h(
                            'div',
                            null,
                            h('b', null, 'Root: '),
                            h(
                                'span',
                                { class: 'mono', title: header.block_root ?? '' },
                                shortenHex(header.block_root ?? ''),
                            ),
                        ),
                        h(
                            'div',
                            null,
                            h('b', null, 'Parent: '),
                            h(
                                'a',
                                {
                                    class: 'linkish mono',
                                    href: `/block/${header.parent_block ?? ''}`,
                                    title: header.parent_block ?? '',
                                },
                                shortenHex(header.parent_block ?? ''),
                            ),
                        ),
                        h(
                            'div',
                            null,
                            h('b', null, 'Created: '),
                            h('span', { class: 'mono' }, formatTimestamp(block.created_at)),
                        ),
                    ),
                ),

                // Transactions card
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
                            h(
                                'tbody',
                                null,
                                ...transactions.map((tx) =>
                                    h(
                                        'tr',
                                        null,
                                        h(
                                            'td',
                                            null,
                                            h(
                                                'a',
                                                {
                                                    class: 'linkish mono',
                                                    href: `/transaction/${tx.hash}`,
                                                    title: tx.hash,
                                                },
                                                shortenHex(tx.hash),
                                            ),
                                        ),
                                        h(
                                            'td',
                                            null,
                                            h(
                                                'span',
                                                { class: 'mono', title: tx.sender ?? '' },
                                                shortenHex(tx.sender ?? ''),
                                            ),
                                            ' \u2192 ',
                                            h(
                                                'span',
                                                { class: 'mono', title: tx.recipient ?? '' },
                                                shortenHex(tx.recipient ?? ''),
                                            ),
                                        ),
                                        h(
                                            'td',
                                            { class: 'amount' },
                                            Number(tx.amount ?? 0).toLocaleString(undefined, {
                                                maximumFractionDigits: 8,
                                            }),
                                        ),
                                        h('td', { class: 'mono' }, formatTimestamp(tx.timestamp)),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
    );
}
