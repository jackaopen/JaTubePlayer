import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import SectionList from './SectionList.js';
import BrowseFeedActions from './BrowseFeedActions.js';
import ProfileColumn from './ProfileColumn.js';
import Tab from './Tab.js';
import ExpandableTab from './ExpandableTab.js';
export default class TwoColumnBrowseResults extends YTNode {
    static type = 'TwoColumnBrowseResults';
    tabs;
    secondary_contents;
    constructor(data) {
        super();
        this.tabs = Parser.parseArray(data.tabs, [Tab, ExpandableTab]);
        this.secondary_contents = Parser.parseItem(data.secondaryContents, [SectionList, BrowseFeedActions, ProfileColumn]);
    }
}
//# sourceMappingURL=TwoColumnBrowseResults.js.map