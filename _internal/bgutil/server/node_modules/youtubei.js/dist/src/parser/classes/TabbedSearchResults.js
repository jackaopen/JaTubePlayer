import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import Tab from './Tab.js';
export default class TabbedSearchResults extends YTNode {
    static type = 'TabbedSearchResults';
    tabs;
    constructor(data) {
        super();
        this.tabs = Parser.parseArray(data.tabs, Tab);
    }
}
//# sourceMappingURL=TabbedSearchResults.js.map