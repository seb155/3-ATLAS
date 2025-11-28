// Version information injected at build time
declare const __APP_VERSION__: string;
declare const __GIT_HASH__: string;
declare const __BUILD_DATE__: string;
declare const __BUILD_NUMBER__: string;

export const VERSION = {
    app: __APP_VERSION__,
    gitHash: __GIT_HASH__,
    buildDate: __BUILD_DATE__,
    buildNumber: __BUILD_NUMBER__,
    full: `v${__APP_VERSION__}+${__GIT_HASH__}#${__BUILD_NUMBER__}`
} as const;

export type VersionInfo = typeof VERSION;
