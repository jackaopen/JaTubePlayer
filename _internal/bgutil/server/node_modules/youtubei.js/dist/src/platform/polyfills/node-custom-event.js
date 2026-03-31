// See https://github.com/nodejs/node/issues/40678#issuecomment-1126944677
export default class CustomEvent extends Event {
    #detail;
    constructor(type, options) {
        super(type, options);
        this.#detail = options?.detail ?? null;
    }
    get detail() {
        return this.#detail;
    }
}
//# sourceMappingURL=node-custom-event.js.map