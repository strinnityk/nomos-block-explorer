import { h } from 'preact';
import { useEffect, useRef, useState } from 'preact/hooks';
import { HEALTH_ENDPOINT } from '../lib/api.js';
import {streamNdjson, withBenignFilter} from '../lib/utils.js';

const STATUS = {
    CONNECTING: 'connecting',
    ONLINE: 'online',
    OFFLINE: 'offline',
};

export default function HealthPill() {
    const [status, setStatus] = useState(STATUS.CONNECTING);
    const pillRef = useRef(null);
    const abortRef = useRef(null);

    // Flash animation whenever status changes
    useEffect(() => {
        const el = pillRef.current;
        if (!el) return;
        el.classList.add('flash');
        const id = setTimeout(() => el.classList.remove('flash'), 750);
        return () => clearTimeout(id);
    }, [status]);

    useEffect(() => {
        abortRef.current?.abort();
        abortRef.current = new AbortController();

        streamNdjson(
            HEALTH_ENDPOINT,
            (item) => {
                if (typeof item?.healthy === 'boolean') {
                    setStatus(item.healthy ? STATUS.ONLINE : STATUS.OFFLINE);
                }
            },
            {
                signal: abortRef.current.signal,
                onError: withBenignFilter(
                    (err) => {
                        if (!abortRef.current.signal.aborted) {
                            console.error('Health stream error:', err);
                            setStatus(STATUS.OFFLINE);
                        }
                    },
                    abortRef.current.signal
                ),
            },
        );

        return () => abortRef.current?.abort();
    }, []);

    const className = 'pill ' + (status === STATUS.ONLINE ? 'online' : status === STATUS.OFFLINE ? 'offline' : '');

    const label = status === STATUS.ONLINE ? 'Online' : status === STATUS.OFFLINE ? 'Offline' : 'Connecting…';

    return h('span', { ref: pillRef, class: className }, label);
}
