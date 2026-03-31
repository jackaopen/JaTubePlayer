import { Context } from '../common';
import { type Parser } from '../parser/parser';
import { Token } from '../token';
export declare const enum Escape {
    Empty = -1,
    StrictOctal = -2,
    EightOrNine = -3,
    InvalidHex = -4,
    OutOfRange = -5
}
export declare function scanString(parser: Parser, context: Context, quote: number): Token;
export declare function parseEscape(parser: Parser, context: Context, first: number, isTemplate?: 0 | 1): number;
export declare function handleStringError(parser: Parser, code: Escape, isTemplate: 0 | 1): void;
