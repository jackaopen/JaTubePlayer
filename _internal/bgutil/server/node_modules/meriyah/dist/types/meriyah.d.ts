import { type Program } from './estree';
import { type Options } from './options';
declare const version: string;
export declare function parseScript(source: string, options?: Options): Program;
export declare function parseModule(source: string, options?: Options): Program;
export declare function parse(source: string, options?: Options): Program;
export { type Options, version };
export type * as ESTree from './estree';
