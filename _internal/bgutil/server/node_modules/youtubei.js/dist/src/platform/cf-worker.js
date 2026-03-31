import { Platform } from '../utils/Utils.js';
import evaluate from './jsruntime/default.js';
import sha1Hash from './polyfills/web-crypto.js';
class Cache {
    #persistent_directory;
    #persistent;
    constructor(persistent = false, persistent_directory) {
        this.#persistent_directory = persistent_directory || '';
        this.#persistent = persistent;
    }
    get cache_dir() {
        return this.#persistent ? this.#persistent_directory : '';
    }
    async get(key) {
        const cache = await caches.open('yt-api');
        const response = await cache.match(key);
        if (!response)
            return undefined;
        return response.arrayBuffer();
    }
    async set(key, value) {
        const cache = await caches.open('yt-api');
        cache.put(key, new Response(value));
    }
    async remove(key) {
        const cache = await caches.open('yt-api');
        await cache.delete(key);
    }
}
Platform.load({
    runtime: 'cf-worker',
    server: true,
    Cache: Cache,
    sha1Hash,
    uuidv4() {
        return crypto.randomUUID();
    },
    eval: evaluate,
    fetch: fetch.bind(globalThis),
    Request: Request,
    Response: Response,
    Headers: Headers,
    FormData: FormData,
    File: File,
    ReadableStream: ReadableStream,
    CustomEvent: CustomEvent
});
export * from './lib.js';
import Innertube from './lib.js';
export default Innertube;
//# sourceMappingURL=cf-worker.js.map