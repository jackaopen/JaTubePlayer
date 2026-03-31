import { LexerState } from './common';
import { Context, type Location } from '../common';
import { type Parser } from '../parser/parser';
export declare const enum CommentType {
    Single = 0,
    Multi = 1,
    HTMLOpen = 2,
    HTMLClose = 3,
    HashBang = 4
}
export declare function skipHashBang(parser: Parser): void;
export declare function skipSingleHTMLComment(parser: Parser, source: string, state: LexerState, context: Context, type: CommentType, start: Location): LexerState;
export declare function skipSingleLineComment(parser: Parser, source: string, state: LexerState, type: CommentType, start: Location): LexerState;
export declare function skipMultiLineComment(parser: Parser, source: string, state: LexerState): LexerState | void;
