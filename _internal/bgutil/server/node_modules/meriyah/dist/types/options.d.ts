import type * as ESTree from './estree';
import { type Token } from './token';
type OnInsertedSemicolon = (pos: number) => any;
export type OnToken = (token: string, start: number, end: number, loc: ESTree.SourceLocation) => any;
export type OnComment = (type: ESTree.CommentType, value: string, start: number, end: number, loc: ESTree.SourceLocation) => any;
export interface Options {
    module?: boolean;
    next?: boolean;
    ranges?: boolean;
    webcompat?: boolean;
    loc?: boolean;
    raw?: boolean;
    globalReturn?: boolean;
    impliedStrict?: boolean;
    preserveParens?: boolean;
    lexical?: boolean;
    source?: string;
    jsx?: boolean;
    onComment?: ESTree.Comment[] | OnComment;
    onInsertedSemicolon?: OnInsertedSemicolon;
    onToken?: Token[] | OnToken;
    uniqueKeyInPattern?: boolean;
}
export type NormalizedOptions = Omit<Options, 'onComment' | 'onToken'> & {
    onComment?: OnComment;
    onToken?: OnToken;
};
export declare function normalizeOptions(rawOptions: Options): NormalizedOptions;
export {};
