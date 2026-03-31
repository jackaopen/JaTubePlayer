import { Platform } from './Utils.js';
export default class UniversalCache {
    #cache;
    constructor(persistent, persistent_directory) {
        this.#cache = new Platform.shim.Cache(persistent, persistent_directory);
    }
    get cache_dir() {
        return this.#cache.cache_dir;
    }
    get(key) {
        return this.#cache.get(key);
    }
    set(key, value) {
        return this.#cache.set(key, value);
    }
    remove(key) {
        return this.#cache.remove(key);
    }
}
//# sourceMappingURL=Cache.js.map