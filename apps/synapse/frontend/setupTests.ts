import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';
import { Buffer } from 'node:buffer';

Object.assign(global, { TextEncoder, TextDecoder });
global.Buffer = Buffer;

// Polyfill for ResizeObserver
global.ResizeObserver = class ResizeObserver {
    observe() { }
    unobserve() { }
    disconnect() { }
};
