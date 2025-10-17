export const API_PREFIX = '/api/v1';

const joinUrl = (...parts) => parts.join('/').replace(/\/{2,}/g, '/');
const encodeId = (id) => encodeURIComponent(String(id));

export const HEALTH_ENDPOINT = joinUrl(API_PREFIX, 'health/stream');
export const BLOCKS_ENDPOINT = joinUrl(API_PREFIX, 'blocks/stream');
export const TRANSACTIONS_ENDPOINT = joinUrl(API_PREFIX, 'transactions/stream');

export const TABLE_SIZE = 10;

export const BLOCK_DETAIL = (id) => joinUrl(API_PREFIX, 'blocks', encodeId(id));
export const TRANSACTION_DETAIL = (id) => joinUrl(API_PREFIX, 'transactions', encodeId(id));
