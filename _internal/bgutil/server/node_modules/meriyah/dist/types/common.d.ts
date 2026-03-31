import { Token } from './token';
import { type Parser } from './parser/parser';
export declare const enum Context {
    None = 0,
    Strict = 1,
    Module = 2,
    InSwitch = 4,
    InGlobal = 8,
    InClass = 16,
    AllowRegExp = 32,
    TaggedTemplate = 64,
    InIteration = 128,
    SuperProperty = 256,
    SuperCall = 512,
    InYieldContext = 1024,
    InAwaitContext = 2048,
    InReturnContext = 4096,
    InArgumentList = 8192,
    InConstructor = 16384,
    InMethodOrFunction = 32768,
    AllowNewTarget = 65536,
    DisallowIn = 131072,
    AllowEscapedKeyword = 262144,
    InStaticBlock = 524288
}
export declare const enum PropertyKind {
    None = 0,
    Method = 1,
    Computed = 2,
    Shorthand = 4,
    Generator = 8,
    Async = 16,
    Static = 32,
    Constructor = 64,
    ClassField = 128,
    Getter = 256,
    Setter = 512,
    Accessor = 1024,
    Extends = 2048,
    Literal = 4096,
    PrivateField = 8192,
    GetSet = 768
}
export declare const enum BindingKind {
    None = 0,
    ArgumentList = 1,
    Empty = 2,
    Variable = 4,
    Let = 8,
    Const = 16,
    Class = 32,
    FunctionLexical = 64,
    FunctionStatement = 128,
    CatchPattern = 256,
    CatchIdentifier = 512,
    Async = 1024,
    Generator = 1024,
    AsyncFunctionLexical = 1088,
    GeneratorFunctionLexical = 1088,
    AsyncGeneratorFunctionLexical = 1088,
    CatchIdentifierOrPattern = 768,
    LexicalOrFunction = 68,
    LexicalBinding = 248
}
export declare const enum Origin {
    None = 0,
    Statement = 1,
    BlockStatement = 2,
    TopLevel = 4,
    Declaration = 8,
    Arrow = 16,
    ForStatement = 32,
    Export = 64
}
export declare const enum AssignmentKind {
    None = 0,
    Assignable = 1,
    CannotAssign = 2
}
export declare const enum DestructuringKind {
    None = 0,
    HasToDestruct = 8,
    CannotDestruct = 16,
    Assignable = 32,
    SeenProto = 64,
    Await = 128,
    Yield = 256
}
export declare const enum Flags {
    None = 0,
    NewLine = 1,
    HasConstructor = 32,
    Octal = 64,
    NonSimpleParameterList = 128,
    HasStrictReserved = 256,
    StrictEvalArguments = 512,
    DisallowCall = 1024,
    HasOptionalChaining = 2048,
    EightAndNine = 4096
}
export declare const enum HoistedClassFlags {
    None = 0,
    Hoisted = 1,
    Export = 2
}
export declare const enum HoistedFunctionFlags {
    None = 0,
    Hoisted = 1,
    Export = 2
}
export declare function matchOrInsertSemicolon(parser: Parser, context: Context): void;
export declare function isValidStrictMode(parser: Parser, index: number, tokenIndex: number, tokenValue: string): 0 | 1;
export declare function optionalBit(parser: Parser, context: Context, t: Token): 0 | 1;
export declare function consumeOpt(parser: Parser, context: Context, t: Token): boolean;
export declare function consume(parser: Parser, context: Context, t: Token): void;
export declare function reinterpretToPattern(parser: Parser, node: any): void;
export declare function validateBindingIdentifier(parser: Parser, context: Context, kind: BindingKind, t: Token, skipEvalArgCheck: 0 | 1): void;
export declare function validateFunctionName(parser: Parser, context: Context, t: Token): void;
export declare function isStrictReservedWord(parser: Parser, context: Context, t: Token): boolean;
export declare function isPropertyWithPrivateFieldKey(expr: any): boolean;
export declare function isValidLabel(parser: Parser, labels: any, name: string, isIterationStatement: 0 | 1): 0 | 1;
export declare function validateAndDeclareLabel(parser: Parser, labels: any, name: string): void;
export declare function isValidIdentifier(context: Context, t: Token): boolean;
export declare function classifyIdentifier(parser: Parser, context: Context, t: Token): any;
export type Location = {
    readonly index: number;
    readonly line: number;
    readonly column: number;
};
export declare function getOwnProperty<T>(object: Record<string | number, T>, key: string | number): T | undefined;
