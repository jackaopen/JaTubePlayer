import { Token } from './token';
import type * as ESTree from './estree';
import { Context, type Location } from './common';
import { Parser } from './parser/parser';
import { type Options } from './options';
import { type Scope } from './parser/scope';
export declare function parseSource(source: string, rawOptions?: Options, context?: Context): ESTree.Program;
export declare function parseModuleItem(parser: Parser, context: Context, scope: Scope | undefined): any;
export declare function parseDirective(parser: Parser, context: Context, expression: ESTree.ArgumentExpression | ESTree.SequenceExpression | ESTree.Expression, token: Token, start: Location): ESTree.ExpressionStatement;
