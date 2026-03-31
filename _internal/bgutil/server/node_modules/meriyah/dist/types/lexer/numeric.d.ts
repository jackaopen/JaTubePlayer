import { Context } from '../common';
import { type Parser } from '../parser/parser';
import { Token } from '../token';
import { NumberKind } from './common';
export declare function scanNumber(parser: Parser, context: Context, kind: NumberKind): Token;
