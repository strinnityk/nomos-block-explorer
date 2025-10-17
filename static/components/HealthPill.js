import { h } from 'preact';
import { useEffect, useRef, useState } from 'preact/hooks';
import { HEALTH_ENDPOINT } from '../lib/api.js';
import { streamNdjson } from '../lib/utils.js';

const STATUS = {
    CONNECTING: 'connecting',
    ONLINE: 'online',
    OFFLINE: 'offline',
};

export default function HealthPill() {
    const [status, setStatus] = useState(STATUS.CONNECTING);
    const pillRef = useRef(null);
    const controllerRef = useRef(null);

    // Flash animation whenever status changes
    useEffect(() => {
        const el = pillRef.current;
        if (!el) return;
        el.classList.add('flash');
        const id = setTimeout(() => el.classList.remove('flash'), 750);
        return () => clearTimeout(id);
    }, [status]);

    useEffect(() => {
        controllerRef.current?.abort();
        controllerRef.current = new AbortController();

        streamNdjson(
            HEALTH_ENDPOINT,
            (item) => {
                if (typeof item?.healthy === 'boolean') {
                    setStatus(item.healthy ? STATUS.ONLINE : STATUS.OFFLINE);
                }
            },
            {
                signal: controllerRef.current.signal,
                onStart: () => setStatus(STATUS.CONNECTING),
                onError: (err) => {
                    if (!controllerRef.current.signal.aborted) {
                        console.error('Health stream error:', err);
                        setStatus(STATUS.OFFLINE);
                    }
                },
            },
        );

        return () => controllerRef.current?.abort();
    }, []);

    const className = 'pill ' + (status === STATUS.ONLINE ? 'online' : status === STATUS.OFFLINE ? 'offline' : '');

    const label = status === STATUS.ONLINE ? 'Online' : status === STATUS.OFFLINE ? 'Offline' : 'Connecting…';

    return h('span', { ref: pillRef, class: className }, label);
}
