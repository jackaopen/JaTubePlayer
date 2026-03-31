import { Token } from './../token';
import { Context } from '../common';
import { type Parser } from '../parser/parser';
export declare function scanIdentifier(parser: Parser, context: Context, isValidAsKeyword: 0 | 1): Token;
export declare function scanUnicodeIdentifier(parser: Parser, context: Context): Token;
export declare function scanIdentifierSlowCase(parser: Parser, context: Context, hasEscape: 0 | 1, isValidAsKeyword: number): Token;
export declare function scanPrivateIdentifier(parser: Parser): Token;
