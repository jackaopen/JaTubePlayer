import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import UniversalWatchCard from './UniversalWatchCard.js';
export default class SecondarySearchContainer extends YTNode {
    static type = 'SecondarySearchContainer';
    target_id;
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents, [UniversalWatchCard]);
    }
}
//# sourceMappingURL=SecondarySearchContainer.js.map