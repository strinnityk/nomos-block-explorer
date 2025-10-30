export const isBenignStreamError = (error, signal) => {
    return false;
};

export const withBenignFilter = (onError, signal) => (error) => {
    if (!isBenignStreamError(error, signal)) onError?.(error);
};

export async function streamNdjson(url, handleItem, { signal, onError = () => {} } = {}) {
    const response = await fetch(url, {
        headers: { accept: 'application/x-ndjson' },
        signal,
        cache: 'no-cache',
    });

    if (!response.ok || !response.body) {
        throw new Error(`Stream failed: ${response.status}`);
    }

    const responseBodyReader = response.body.getReader();
    const textDecoder = new TextDecoder();
    let buffer = '';

    while (true) {
        let chunk;
        try {
            chunk = await responseBodyReader.read();
        } catch (error) {
            if (signal?.aborted) return;
            onError(error);
            break;
        }
        const { value, done } = chunk;
        if (done) break;

        buffer += textDecoder.decode(value, { stream: true });

        let newlineIndex;
        while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
            const line = buffer.slice(0, newlineIndex).trim();
            buffer = buffer.slice(newlineIndex + 1);
            if (!line) continue;
            try {
                handleItem(JSON.parse(line));
            } catch (error) {
                onError(error);
            }
        }
    }

    const trailing = buffer.trim();
    if (trailing) {
        try {
            handleItem(JSON.parse(trailing));
        } catch (error) {
            onError(error);
        }
    }
}

export const shortenHex = (hexString, left = 10, right = 8) => {
    if (!hexString) return '';
    return hexString.length <= left + right + 1 ? hexString : `${hexString.slice(0, left)}…${hexString.slice(-right)}`;
};

export function formatTimestamp(timestamp) {
    if (timestamp == null) return '';
    const date =
        typeof timestamp === 'number' ? new Date(timestamp < 1e12 ? timestamp * 1000 : timestamp) : new Date(timestamp);

    if (Number.isNaN(date.getTime())) return '';
    return date.toLocaleString(undefined, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
}

export function ensureFixedRowCount(tableBody, columnCount, targetRowCount) {
    // remove existing placeholder rows
    for (let i = tableBody.rows.length - 1; i >= 0; i--) {
        if (tableBody.rows[i].classList.contains('ph')) tableBody.deleteRow(i);
    }

    // count non-placeholder rows
    let realRowCount = 0;
    for (const row of tableBody.rows) {
        if (!row.classList.contains('ph')) realRowCount++;
    }

    // append placeholders to reach target count
    for (let i = 0; i < targetRowCount - realRowCount; i++) {
        const tr = document.createElement('tr');
        tr.className = 'ph';
        for (let c = 0; c < columnCount; c++) {
            const td = document.createElement('td');
            td.innerHTML = '&nbsp;';
            tr.appendChild(td);
        }
        tableBody.appendChild(tr);
    }
}
