import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Tab from './Tab.js';
export default class SingleColumnBrowseResults extends YTNode {
    static type = 'SingleColumnBrowseResults';
    tabs;
    constructor(data) {
        super();
        this.tabs = Parser.parseArray(data.tabs, Tab);
    }
}
//# sourceMappingURL=SingleColumnBrowseResults.js.map