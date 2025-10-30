const API_PREFIX = '/api/v1';

const joinUrl = (...parts) => parts.join('/').replace(/\/{2,}/g, '/');
const encodeId = (id) => encodeURIComponent(String(id));

const HEALTH_ENDPOINT = joinUrl(API_PREFIX, 'health/stream');

const TRANSACTION_DETAIL_BY_ID = (id) => joinUrl(API_PREFIX, 'transactions', encodeId(id));
const TRANSACTIONS_STREAM = joinUrl(API_PREFIX, 'transactions/stream');

const BLOCK_DETAIL_BY_ID = (id) => joinUrl(API_PREFIX, 'blocks', encodeId(id));
const BLOCKS_STREAM = joinUrl(API_PREFIX, 'blocks/stream');

export const API = {
    HEALTH_ENDPOINT,
    TRANSACTION_DETAIL_BY_ID,
    TRANSACTIONS_STREAM,
    BLOCK_DETAIL_BY_ID,
    BLOCKS_STREAM,
};

const BLOCK_DETAIL = (id) => joinUrl('/blocks', encodeId(id));
const TRANSACTION_DETAIL = (id) => joinUrl('/transactions', encodeId(id));

export const PAGE = {
    BLOCK_DETAIL,
    TRANSACTION_DETAIL,
};
