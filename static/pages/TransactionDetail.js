import { h } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import { shortenHex, formatTimestamp } from '../lib/utils.js?dev=1';
import { TRANSACTION_DETAIL } from '../lib/api.js?dev=1';

export default function TransactionDetail({ params: routeParams }) {
    const transactionId = routeParams[0];

    const [transaction, setTransaction] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const controller = new AbortController();

        (async () => {
            try {
                const response = await fetch(TRANSACTION_DETAIL(transactionId), {
                    signal: controller.signal,
                    cache: 'no-cache',
                });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const data = await response.json();
                setTransaction(data);
            } catch (err) {
                if (!controller.signal.aborted) {
                    setError(err.message || 'Request failed');
                }
            }
        })();

        return () => controller.abort();
    }, [transactionId]);

    return h(
        'main',
        { class: 'wrap' },

        h(
            'header',
            { style: 'display:flex; gap:12px; align-items:center; margin:12px 0;' },
            h('a', { class: 'linkish', href: '/' }, '← Back'),
            h('h1', { style: 'margin:0' }, `Transaction ${shortenHex(transactionId, 12, 12)}`),
        ),

        error && h('p', { style: 'color:#ff8a8a' }, `Error: ${error}`),
        !transaction && !error && h('p', null, 'Loading…'),

        transaction &&
            h(
                'div',
                { class: 'card', style: 'margin-top:12px;' },
                h('div', { class: 'card-header' }, h('strong', null, 'Overview')),
                h(
                    'div',
                    { style: 'padding:12px 14px' },
                    h(
                        'div',
                        null,
                        h('b', null, 'Hash: '),
                        h('span', { class: 'mono', title: transaction.hash }, shortenHex(transaction.hash)),
                    ),
                    h(
                        'div',
                        null,
                        h('b', null, 'From: '),
                        h(
                            'span',
                            { class: 'mono', title: transaction.sender ?? '' },
                            shortenHex(transaction.sender ?? ''),
                        ),
                    ),
                    h(
                        'div',
                        null,
                        h('b', null, 'To: '),
                        h(
                            'span',
                            { class: 'mono', title: transaction.recipient ?? '' },
                            shortenHex(transaction.recipient ?? ''),
                        ),
                    ),
                    h(
                        'div',
                        null,
                        h('b', null, 'Amount: '),
                        h(
                            'span',
                            { class: 'amount' },
                            Number(transaction.amount ?? 0).toLocaleString(undefined, {
                                maximumFractionDigits: 8,
                            }),
                        ),
                    ),
                    h(
                        'div',
                        null,
                        h('b', null, 'Time: '),
                        h('span', { class: 'mono' }, formatTimestamp(transaction.timestamp)),
                    ),
                    transaction.block_root &&
                        h(
                            'div',
                            null,
                            h('b', null, 'Block: '),
                            h(
                                'a',
                                {
                                    class: 'linkish mono',
                                    href: `/block/${transaction.block_root}`,
                                    title: transaction.block_root,
                                },
                                shortenHex(transaction.block_root),
                            ),
                        ),
                ),
            ),
    );
}
