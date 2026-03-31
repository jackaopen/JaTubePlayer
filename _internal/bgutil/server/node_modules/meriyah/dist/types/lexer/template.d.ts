import { Context } from '../common';
import { type Parser } from '../parser/parser';
import { Token } from '../token';
export declare function scanTemplate(parser: Parser, context: Context): Token;
export declare function scanTemplateTail(parser: Parser, context: Context): Token;
