import { h } from 'preact';
import BlocksTable from '../components/BlocksTable.js';
import TransactionsTable from '../components/TransactionsTable.js';

export default function HomeView() {
    return h(
        'main',
        { class: 'wrap' },
        h('section', { class: 'two-columns twocol' }, h(BlocksTable, {}), h(TransactionsTable, {})),
    );
}
