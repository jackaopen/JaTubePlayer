import { Errors } from '../errors';
import { type Location, Context, BindingKind, Origin } from '../common';
import { type Parser } from './parser';
export declare const enum ScopeKind {
    ForStatement = 1,
    Block = 2,
    CatchStatement = 4,
    SwitchStatement = 8,
    TryStatement = 16,
    CatchBlock = 32,
    FunctionBody = 64,
    FunctionRoot = 128,
    FunctionParams = 256,
    ArrowParams = 512
}
interface ScopeError {
    type: Errors;
    params: string[];
    start: Location;
    end: Location;
}
export declare class Scope {
    readonly parser: Parser;
    readonly type: ScopeKind;
    readonly parent?: Scope | undefined;
    scopeError?: ScopeError;
    variableBindings: Map<string, BindingKind>;
    constructor(parser: Parser, type?: ScopeKind, parent?: Scope | undefined);
    createChildScope(type?: ScopeKind): Scope;
    addVarOrBlock(context: Context, name: string, kind: BindingKind, origin: Origin): void;
    addVarName(context: Context, name: string, kind: BindingKind): void;
    hasVariable(name: string): boolean;
    addBlockName(context: Context, name: string, kind: BindingKind, origin: Origin): void;
    recordScopeError(type: Errors, ...params: string[]): void;
    reportScopeError(): void;
}
export declare function createArrowHeadParsingScope(parser: Parser, context: Context, value: string): Scope;
export {};
