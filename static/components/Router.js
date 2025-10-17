import { h } from 'preact';
import { useEffect, useState } from 'preact/hooks';

export default function AppRouter({ routes }) {
    const [match, setMatch] = useState(() => resolveRoute(location.pathname, routes));

    useEffect(() => {
        const handlePopState = () => setMatch(resolveRoute(location.pathname, routes));

        const handleLinkClick = (event) => {
            // Only intercept unmodified left-clicks
            if (event.defaultPrevented || event.button !== 0) return;
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

            const anchor = event.target.closest?.('a[href]');
            if (!anchor) return;

            // Respect explicit navigation hints
            if (anchor.target && anchor.target !== '_self') return;
            if (anchor.hasAttribute('download')) return;
            if (anchor.getAttribute('rel')?.includes('external')) return;
            if (anchor.dataset.external === 'true' || anchor.dataset.noRouter === 'true') return;

            const href = anchor.getAttribute('href');
            if (!href) return;

            // Allow in-page, mailto, and other schemes to pass through
            if (href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) return;

            // Different origin → let the browser handle it
            if (anchor.origin !== location.origin) return;

            // Likely a static asset (e.g., ".css", ".png") → let it pass
            if (/\.[a-z0-9]+($|\?)/i.test(href)) return;

            event.preventDefault();
            history.pushState({}, '', href);
            setMatch(resolveRoute(location.pathname, routes));
        };

        window.addEventListener('popstate', handlePopState);
        document.addEventListener('click', handleLinkClick);

        return () => {
            window.removeEventListener('popstate', handlePopState);
            document.removeEventListener('click', handleLinkClick);
        };
    }, [routes]);

    const View = match?.view ?? NotFound;
    return h(View, { params: match?.params ?? [] });
}

function resolveRoute(pathname, routes) {
    for (const route of routes) {
        const result = pathname.match(route.pattern);
        if (result) return { view: route.view, params: result.slice(1) };
    }
    return null;
}

function NotFound() {
    return h('main', { class: 'wrap' }, h('h1', null, 'Not found'));
}
