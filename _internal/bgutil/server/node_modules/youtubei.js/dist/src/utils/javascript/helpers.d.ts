import type { ESTree } from 'meriyah';
import type { JsAnalyzer } from './JsAnalyzer.js';
export declare const WALK_STOP: unique symbol;
export declare const jsBuiltIns: Set<string>;
export declare const indent = "  ";
export type AstVisitResult = boolean | typeof WALK_STOP | void;
export type AstVisitFn = (node: ESTree.Node, parent: ESTree.Node | null, ancestors: ESTree.Node[]) => AstVisitResult;
export interface AstVisitObject {
    /**
     * Callback invoked when an AST node is entered.
     * @param node - Current AST node being visited.
     * @param parent - Parent of the current AST node, or null if it's the root.
     * @param ancestors - Array of ancestor nodes, starting from the root down to the parent.
     * @returns
     * - `true` to skip traversing this node's children.
     * - `WALK_STOP` to halt the entire traversal.
     * - `void`/`undefined` to continue normal traversal.
     */
    enter?(node: ESTree.Node, parent: ESTree.Node | null, ancestors: ESTree.Node[]): AstVisitResult;
    /**
     * Callback invoked when an AST node is exited.
     * @param node - Current AST node being exited.
     * @param parent - Parent of the current AST node, or null if it's the root.
     * @param ancestors - Array of ancestor nodes, starting from the root down to the parent.
     * @returns
     * - `WALK_STOP` to halt the entire traversal.
     * - `void`/`undefined` to continue normal traversal.
     */
    leave?(node: ESTree.Node, parent: ESTree.Node | null, ancestors: ESTree.Node[]): AstVisitResult;
}
export type AstVisitor = AstVisitFn | AstVisitObject;
/**
 * Performs a non-recursive traversal of an ESTree AST.
 * @param root - Root AST node to start the traversal from.
 * @param visitor - Callbacks invoked when nodes are entered or left.
 * @remarks
 * - If it returns `WALK_STOP`, the entire traversal is halted.
 * - Why did I not use some AST walker library instead?: They're too slow.
 */
export declare function walkAst(root: ESTree.Node, visitor: AstVisitor): void;
/**
 * Returns the source range of an ESTree node as a tuple of start and end positions.
 * @param node - The ESTree node to extract the source range from.
 * @returns A tuple `[start, end]` representing the source range, or `null` if unavailable.
 */
export declare function getNodeSourceRange(node: ESTree.Node | null | undefined): [number, number] | null;
/**
 * Extracts the source code corresponding to a given AST node.
 * @param node - The AST node to extract source from.
 * @param source - The original source code.
 * @returns The source code corresponding to the node, or null if not available.
 */
export declare function extractNodeSource(node: ESTree.Node | null | undefined, source: string): string | null;
/**
 * Converts a member expression into its dot/bracket string form.
 * @param memberExpression - Member expression node to stringify.
 * @param source - Original source code for range lookups.
 */
export declare function memberToString(memberExpression: ESTree.Node, source: string): string | null;
/**
 * Retrieves the base identifier for a member expression chain.
 * @param memberExpression - Member expression whose root should be resolved.
 * @param source - Original source code for range lookups.
 */
export declare function memberBaseName(memberExpression: ESTree.MemberExpression, source: string): string | null;
/**
 * Analyzes an AST node to determine if it's a function call or a function
 * declaration. Based on that, it then creates a new JavaScript function as
 * a string. This new function acts as a wrapper, taking a single 'input'
 * argument and forwarding it to the original function call.
 *
 * Currently can handle:
 * - `CallExpression`: Creates a wrapper that invokes the function being called in the expression.
 * - `VariableDeclarator` with a `FunctionExpression`: Creates a wrapper that calls the declared function.
 *
 * @param analyzer - The `JSAnalyzer` instance, used to resolve context like declared variables.
 * @param name - The name for the new wrapper function to be created.
 * @param node - The ESTree node.
 * @todo Look for edge cases.
 */
export declare function createWrapperFunction(analyzer: JsAnalyzer, name: string, node: ESTree.Node): string | undefined;
