import { Token } from '../token';
import { type Parser } from '../parser/parser';
export declare const enum LexerState {
    None = 0,
    NewLine = 1,
    LastIsCR = 4
}
export declare const enum NumberKind {
    ImplicitOctal = 1,
    Binary = 2,
    Octal = 4,
    Hex = 8,
    Decimal = 16,
    NonOctalDecimal = 32,
    Float = 64,
    ValidBigIntKind = 128,
    DecimalNumberKind = 48
}
export declare function advanceChar(parser: Parser): number;
export declare function consumePossibleSurrogatePair(parser: Parser): number;
export declare function consumeLineFeed(parser: Parser, state: LexerState): void;
export declare function scanNewLine(parser: Parser): void;
export declare function isExoticECMAScriptWhitespace(ch: number): boolean;
export declare function toHex(code: number): number;
export declare function convertTokenType(t: Token): string;
