import type { ESTree } from 'meriyah';
export declare function sigMatcher(node: ESTree.Node): false | ESTree.CallExpression;
export declare function nMatcher(node: ESTree.Node): false | ESTree.Identifier;
export declare function timestampMatcher(node: ESTree.Node): boolean;
