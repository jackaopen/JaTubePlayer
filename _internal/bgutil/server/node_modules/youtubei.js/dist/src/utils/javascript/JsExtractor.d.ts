import type { JsAnalyzer } from './JsAnalyzer.js';
export type SideEffectMode = 'strict' | 'loose';
export interface SideEffectPolicyOptions {
    /**
     * Determines how strictly side-effect detection should behave.
     * Use `"loose"` to allow benign computed expressions.
     */
    mode?: SideEffectMode;
}
export interface EmitterOptions {
    /**
     * The maximum depth to traverse when emitting dependencies.
     * If not specified, there is no limit on the depth.
     */
    maxDepth?: number;
    /**
     * When true or configured, replace unsafe initializers (calls, `new`, etc.)
     * with `undefined` to avoid executing side-effectful code.
     * Use `{ mode: 'loose' }` to allow a broader set of expressions.
     */
    disallowSideEffectInitializers?: boolean | SideEffectPolicyOptions;
    /**
     * When true, emit a single `var` declaration for every variable
     * encountered, even if it originally had an initializer.
     */
    forceVarPredeclaration?: boolean;
    /**
     * When true, also export raw values of matched nodes.
     */
    exportRawValues?: boolean;
    /**
     * Array of names to skip emitting code/deps for, but still export the raw value.
     */
    rawValueOnly?: string[];
}
export interface BuildScriptResult {
    /**
     * The generated output script as a string.
     */
    output: string;
    /**
     * An array of exported variable names.
     */
    exported: string[];
    /**
     * An object mapping exported variable names to their raw values, if `exportRawValues` was enabled.
     */
    exportedRawValues?: Record<string, any>;
}
/**
 * Class responsible for extracting and emitting JavaScript code snippets
 * based on analysis results from a `JsAnalyzer` instance.
 */
export declare class JsExtractor {
    private analyzer;
    constructor(analyzer: JsAnalyzer);
    /**
     * Checks if all provided arguments are safe initializers.
     * @param args - The arguments to check.
     * @param mode - The side effect mode to use ('strict' or 'loose').
     */
    private areSafeArgs;
    /**
     * Determines if a given AST node is a safe initializer without side effects.
     * @param node - The AST node to evaluate.
     * @param mode - The side effect mode to use ('strict' or 'loose').
     */
    private isSafeInitializer;
    /**
     * Provides a fallback initializer string based on the type of the initializer node.
     * @TODO: Check more cases.
     * @param init - The initializer expression to evaluate.
     */
    private getInitializerFallback;
    /**
     * Renders an AST node to JavaScript source code, with special handling for variable declarators.
     * @param node - The ESTree node to render.
     * @param preDeclared - Whether the variable has been previously declared.
     * @param options - Configuration options for the emitter.
     */
    private renderNode;
    /**
     * Processes extracted matches from the analyzer, handles dependencies, predeclares
     * variables as needed, and generates an IIFE-wrapped output string containing the
     * code snippets and exported variables.
     * @param config - Configuration options for the emitter.
     */
    buildScript(config: EmitterOptions): BuildScriptResult;
}
