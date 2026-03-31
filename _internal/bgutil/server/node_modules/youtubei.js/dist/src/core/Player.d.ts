import type { FetchFunction, ICache } from '../types/index.js';
import type { BuildScriptResult } from '../utils/javascript/JsExtractor.js';
interface PlayerInitializationOptions {
    cache?: ICache;
    signature_timestamp: number;
    data: BuildScriptResult;
}
/**
 * Represents YouTube's player script. This is required to decipher signatures.
 */
export default class Player {
    player_id: string;
    signature_timestamp: number;
    data?: BuildScriptResult | undefined;
    po_token?: string;
    constructor(player_id: string, signature_timestamp: number, data?: BuildScriptResult | undefined);
    static create(cache: ICache | undefined, fetch?: FetchFunction, po_token?: string, player_id?: string): Promise<Player>;
    decipher(url?: string, signature_cipher?: string, cipher?: string, this_response_nsig_cache?: Map<string, string>): Promise<string>;
    static fromCache(cache: ICache, player_id: string): Promise<Player | null>;
    static fromSource(player_id: string, options: PlayerInitializationOptions): Promise<Player>;
    cache(cache?: ICache): Promise<void>;
    get url(): string;
    static get LIBRARY_VERSION(): number;
}
export {};
