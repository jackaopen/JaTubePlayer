import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class Endscreen extends YTNode {
    static type = 'Endscreen';
    elements;
    start_ms;
    constructor(data) {
        super();
        this.elements = Parser.parseArray(data.elements);
        this.start_ms = data.startMs;
    }
}
//# sourceMappingURL=Endscreen.js.map