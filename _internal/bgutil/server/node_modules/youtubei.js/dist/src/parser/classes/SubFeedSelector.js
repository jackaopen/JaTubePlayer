import { Parser } from '../index.js';
import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
import SubFeedOption from './SubFeedOption.js';
export default class SubFeedSelector extends YTNode {
    static type = 'SubFeedSelector';
    title;
    options;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.options = Parser.parseArray(data.options, SubFeedOption);
    }
}
//# sourceMappingURL=SubFeedSelector.js.map