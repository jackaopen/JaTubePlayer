// Node.js Platform Support
import { ReadableStream } from 'stream/web';
import { Platform } from '../utils/Utils.js';
import crypto from 'crypto';
import path from 'path';
import os from 'os';
import fs from 'fs/promises';
import CustomEvent from './polyfills/node-custom-event.js';
import { fileURLToPath } from 'url';
import evaluate from './jsruntime/default.js';
const meta_url = import.meta.url;
const is_cjs = !meta_url;
const __dirname__ = is_cjs ? __dirname : path.dirname(fileURLToPath(meta_url));
class Cache {
    #persistent_directory;
    #persistent;
    constructor(persistent = false, persistent_directory) {
        this.#persistent_directory = persistent_directory || Cache.default_persistent_directory;
        this.#persistent = persistent;
    }
    static get temp_directory() {
        return `${os.tmpdir()}/youtubei.js`;
    }
    static get default_persistent_directory() {
        return path.resolve(__dirname__, '..', '..', '.cache', 'youtubei.js');
    }
    get cache_dir() {
        return this.#persistent ? this.#persistent_directory : Cache.temp_directory;
    }
    async #createCache() {
        const dir = this.cache_dir;
        try {
            const cwd = await fs.stat(dir);
            if (!cwd.isDirectory())
                throw new Error('An unexpected file was found in place of the cache directory');
        }
        catch (e) {
            if (e?.code === 'ENOENT')
                await fs.mkdir(dir, { recursive: true });
            else
                throw e;
        }
    }
    async get(key) {
        await this.#createCache();
        const file = path.resolve(this.cache_dir, key);
        try {
            const stat = await fs.stat(file);
            if (stat.isFile()) {
                const data = await fs.readFile(file);
                return data.buffer;
            }
            throw new Error('An unexpected file was found in place of the cache key');
        }
        catch (e) {
            if (e?.code === 'ENOENT')
                return undefined;
            throw e;
        }
    }
    async set(key, value) {
        await this.#createCache();
        const file = path.resolve(this.cache_dir, key);
        await fs.writeFile(file, new Uint8Array(value));
    }
    async remove(key) {
        await this.#createCache();
        const file = path.resolve(this.cache_dir, key);
        try {
            await fs.unlink(file);
        }
        catch (e) {
            if (e?.code === 'ENOENT')
                return;
            throw e;
        }
    }
}
Platform.load({
    runtime: 'node',
    server: true,
    Cache: Cache,
    sha1Hash: async (data) => {
        return crypto.createHash('sha1').update(data).digest('hex');
    },
    uuidv4() {
        return crypto.randomUUID();
    },
    eval: evaluate,
    fetch: globalThis.fetch,
    Request: globalThis.Request,
    Response: globalThis.Response,
    Headers: globalThis.Headers,
    FormData: globalThis.FormData,
    File: globalThis.File,
    ReadableStream: ReadableStream,
    CustomEvent: CustomEvent
});
export * from './lib.js';
import Innertube from './lib.js';
export default Innertube;
//# sourceMappingURL=node.js.map