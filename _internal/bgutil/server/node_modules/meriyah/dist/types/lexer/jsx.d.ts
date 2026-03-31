import { Token } from '../token';
import { type Context } from '../common';
import { type Parser } from '../parser/parser';
export declare function scanJSXAttributeValue(parser: Parser, context: Context): Token;
export declare function nextJSXToken(parser: Parser): void;
export declare function rescanJSXIdentifier(parser: Parser): Token;
