import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class WatchCardSectionSequence extends YTNode {
    static type = 'WatchCardSectionSequence';
    lists;
    constructor(data) {
        super();
        this.lists = Parser.parseArray(data.lists);
    }
}
//# sourceMappingURL=WatchCardSectionSequence.js.map