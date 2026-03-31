import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ChipCloudChip from './ChipCloudChip.js';
export default class FeedFilterChipBar extends YTNode {
    static type = 'FeedFilterChipBar';
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents, ChipCloudChip);
    }
}
//# sourceMappingURL=FeedFilterChipBar.js.map