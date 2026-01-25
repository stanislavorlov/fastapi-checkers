import { InjectionToken } from '@angular/core';

export const USER_AGENT = new InjectionToken<string>('USER_AGENT');

// Use globalThis to ensure this is a singleton across potentially multiple bundles in the same process
if (!(globalThis as any).requestContext) {
    try {
        const { AsyncLocalStorage } = require('node:async_hooks');
        (globalThis as any).requestContext = new AsyncLocalStorage();
    } catch (e) {
        // Fallback for browser
        (globalThis as any).requestContext = {
            getStore: () => null,
            run: (context: any, fn: () => any) => fn()
        };
    }
}
export const requestContext = (globalThis as any).requestContext;
