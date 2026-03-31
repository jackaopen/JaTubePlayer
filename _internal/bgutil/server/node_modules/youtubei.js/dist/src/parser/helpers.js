import * as Log from '../utils/Log.js';
import { deepCompare, ParsingError } from '../utils/Utils.js';
const isObserved = Symbol('ObservedArray.isObserved');
export class YTNode {
    static type = 'YTNode';
    type;
    constructor() {
        this.type = this.constructor.type;
    }
    /**
     * Check if the node is of the given type.
     * @param types - The type to check
     * @returns whether the node is of the given type
     */
    is(...types) {
        return types.some((type) => this.type === type.type);
    }
    /**
     * Cast to one of the given types.
     * @param types - The types to cast to
     * @returns The node cast to one of the given types
     * @throws {ParsingError} If the node is not of the given type
     */
    as(...types) {
        if (!this.is(...types)) {
            throw new ParsingError(`Cannot cast ${this.type} to one of ${types.map((t) => t.type).join(', ')}`);
        }
        return this;
    }
    /**
     * Check for a key without asserting the type.
     * @param key - The key to check
     * @returns Whether the node has the key
     */
    hasKey(key) {
        return Reflect.has(this, key);
    }
    /**
     * Assert that the node has the given key and return it.
     * @param key - The key to check
     * @returns The value of the key wrapped in a Maybe
     * @throws {ParsingError} If the node does not have the key
     */
    key(key) {
        if (!this.hasKey(key)) {
            throw new ParsingError(`Missing key ${key}`);
        }
        return new Maybe(this[key]);
    }
}
const MAYBE_TAG = 'Maybe';
/**
 * A wrapper class that provides type-safe access to a value.
 */
export class Maybe {
    #value;
    constructor(value) {
        this.#value = value;
    }
    #checkPrimitive(type) {
        return typeof this.#value === type;
    }
    #assertPrimitive(type) {
        if (!this.#checkPrimitive(type)) {
            throw new TypeError(`Expected ${type}, got ${this.typeof}`);
        }
        return this.#value;
    }
    get typeof() {
        return typeof this.#value;
    }
    string() {
        return this.#assertPrimitive('string');
    }
    isString() {
        return this.#checkPrimitive('string');
    }
    number() {
        return this.#assertPrimitive('number');
    }
    isNumber() {
        return this.#checkPrimitive('number');
    }
    bigint() {
        return this.#assertPrimitive('bigint');
    }
    isBigint() {
        return this.#checkPrimitive('bigint');
    }
    boolean() {
        return this.#assertPrimitive('boolean');
    }
    isBoolean() {
        return this.#checkPrimitive('boolean');
    }
    symbol() {
        return this.#assertPrimitive('symbol');
    }
    isSymbol() {
        return this.#checkPrimitive('symbol');
    }
    undefined() {
        return this.#assertPrimitive('undefined');
    }
    isUndefined() {
        return this.#checkPrimitive('undefined');
    }
    null() {
        if (this.#value !== null)
            throw new TypeError(`Expected null, got ${typeof this.#value}`);
        return this.#value;
    }
    isNull() {
        return this.#value === null;
    }
    object() {
        return this.#assertPrimitive('object');
    }
    isObject() {
        return this.#checkPrimitive('object');
    }
    // eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
    function() {
        return this.#assertPrimitive('function');
    }
    isFunction() {
        return this.#checkPrimitive('function');
    }
    /**
     * Get the value as an array.
     * @returns the value as any[].
     * @throws If the value is not an array.
     */
    array() {
        if (!Array.isArray(this.#value)) {
            throw new TypeError(`Expected array, got ${typeof this.#value}`);
        }
        return this.#value;
    }
    /**
     * More typesafe variant of {@link Maybe#array}.
     * @returns a proxied array which returns all the values as {@link Maybe}.
     * @throws {TypeError} If the value is not an array
     */
    arrayOfMaybe() {
        const arrayProps = [];
        return new Proxy(this.array(), {
            get(target, prop) {
                if (Reflect.has(arrayProps, prop)) {
                    return Reflect.get(target, prop);
                }
                return new Maybe(Reflect.get(target, prop));
            }
        });
    }
    /**
     * Check whether the value is an array.
     * @returns whether the value is an array.
     */
    isArray() {
        return Array.isArray(this.#value);
    }
    /**
     * Get the value as a YTNode.
     * @returns the value as a YTNode.
     * @throws If the value is not a YTNode.
     */
    node() {
        if (!(this.#value instanceof YTNode)) {
            throw new TypeError(`Expected YTNode, got ${this.#value.constructor.name}`);
        }
        return this.#value;
    }
    /**
     * Check if the value is a YTNode.
     * @returns Whether the value is a YTNode.
     */
    isNode() {
        return this.#value instanceof YTNode;
    }
    /**
     * Get the value as a YTNode of the given type.
     * @param types - The type(s) to cast to.
     * @returns The node cast to the given type.
     * @throws If the node is not of the given type.
     */
    nodeOfType(...types) {
        return this.node().as(...types);
    }
    /**
     * Check if the value is a YTNode of the given type.
     * @param types - the type(s) to check.
     * @returns Whether the value is a YTNode of the given type.
     */
    isNodeOfType(...types) {
        return this.isNode() && this.node().is(...types);
    }
    /**
     * Get the value as an ObservedArray.
     * @returns the value of the Maybe as a ObservedArray.
     */
    observed() {
        if (!this.isObserved()) {
            throw new TypeError(`Expected ObservedArray, got ${typeof this.#value}`);
        }
        return this.#value;
    }
    /**
     * Check if the value is an ObservedArray.
     */
    isObserved() {
        return this.#value?.[isObserved];
    }
    /**
     * Get the value of the Maybe as a SuperParsedResult.
     * @returns the value as a SuperParsedResult.
     * @throws If the value is not a SuperParsedResult.
     */
    parsed() {
        if (!(this.#value instanceof SuperParsedResult)) {
            throw new TypeError(`Expected SuperParsedResult, got ${typeof this.#value}`);
        }
        return this.#value;
    }
    /**
     * Is the result a SuperParsedResult?
     */
    isParsed() {
        return this.#value instanceof SuperParsedResult;
    }
    /**
     * @deprecated
     * This call is not meant to be used outside of debugging. Please use the specific type getter instead.
     */
    any() {
        Log.warn(MAYBE_TAG, 'This call is not meant to be used outside of debugging. Please use the specific type getter instead.');
        return this.#value;
    }
    /**
     * Get the node as an instance of the given class.
     * @param type - The type to check.
     * @returns the value as the given type.
     * @throws If the node is not of the given type.
     */
    instanceof(type) {
        if (!this.isInstanceof(type)) {
            throw new TypeError(`Expected instance of ${type.name}, got ${this.#value.constructor.name}`);
        }
        return this.#value;
    }
    /**
     * Check if the node is an instance of the given class.
     * @param type - The type to check.
     * @returns Whether the node is an instance of the given type.
     */
    isInstanceof(type) {
        return this.#value instanceof type;
    }
}
/**
 * Represents a parsed response in an unknown state. Either a YTNode or a YTNode[] or null.
 */
export class SuperParsedResult {
    #result;
    constructor(result) {
        this.#result = result;
    }
    get is_null() {
        return this.#result === null;
    }
    get is_array() {
        return !this.is_null && Array.isArray(this.#result);
    }
    get is_node() {
        return !this.is_array;
    }
    array() {
        if (!this.is_array) {
            throw new TypeError('Expected an array, got a node');
        }
        return this.#result;
    }
    item() {
        if (!this.is_node) {
            throw new TypeError('Expected a node, got an array');
        }
        return this.#result;
    }
}
/**
 * Creates an observed array that provides additional utility methods for array manipulation and filtering.
 * @template T - Type extending YTNode
 * @param obj - Array to be observed
 */
export function observe(obj) {
    return new Proxy(obj, {
        get(target, prop) {
            if (prop == 'get') {
                return (rule, del_item) => (target.find((obj, index) => {
                    const match = deepCompare(rule, obj);
                    if (match && del_item) {
                        target.splice(index, 1);
                    }
                    return match;
                }));
            }
            if (prop == isObserved) {
                return true;
            }
            if (prop == 'getAll') {
                return (rule, del_items) => (target.filter((obj, index) => {
                    const match = deepCompare(rule, obj);
                    if (match && del_items) {
                        target.splice(index, 1);
                    }
                    return match;
                }));
            }
            if (prop == 'matchCondition') {
                return (condition) => (target.find((obj) => {
                    return condition(obj);
                }));
            }
            if (prop == 'filterType') {
                return (...types) => {
                    return observe(target.filter((node) => {
                        return !!node.is(...types);
                    }));
                };
            }
            if (prop == 'firstOfType') {
                return (...types) => {
                    return target.find((node) => {
                        return !!node.is(...types);
                    });
                };
            }
            if (prop == 'first') {
                return () => target[0];
            }
            if (prop == 'as') {
                return (...types) => {
                    return observe(target.map((node) => {
                        if (node.is(...types))
                            return node;
                        throw new ParsingError(`Expected node of any type ${types.map((type) => type.type).join(', ')}, got ${node.type}`);
                    }));
                };
            }
            if (prop == 'remove') {
                return (index) => target.splice(index, 1);
            }
            return Reflect.get(target, prop);
        }
    });
}
export class Memo extends Map {
    getType(...types) {
        types = types.flat();
        return observe(types.flatMap((type) => (this.get(type.type) || [])));
    }
}
//# sourceMappingURL=helpers.js.map