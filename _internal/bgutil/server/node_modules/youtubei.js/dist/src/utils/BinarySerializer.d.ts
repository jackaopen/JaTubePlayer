export declare const MAGIC_HEADER = 5849684;
export declare const VERSION = 1;
export declare function serialize(data: any): ArrayBuffer;
export declare function deserialize<T>(buffer: Uint8Array): T;
