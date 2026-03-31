import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class BackstagePostThread extends YTNode {
    static type = 'BackstagePostThread';
    post;
    constructor(data) {
        super();
        this.post = Parser.parseItem(data.post);
    }
}
//# sourceMappingURL=BackstagePostThread.js.map