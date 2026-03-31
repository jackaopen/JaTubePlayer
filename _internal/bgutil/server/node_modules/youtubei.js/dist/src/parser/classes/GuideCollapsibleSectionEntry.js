import * as Parser from '../parser.js';
import { YTNode } from '../helpers.js';
export default class GuideCollapsibleSectionEntry extends YTNode {
    static type = 'GuideCollapsibleSectionEntry';
    header_entry;
    expander_icon;
    collapser_icon;
    section_items;
    constructor(data) {
        super();
        this.header_entry = Parser.parseItem(data.headerEntry);
        this.expander_icon = data.expanderIcon.iconType;
        this.collapser_icon = data.collapserIcon.iconType;
        this.section_items = Parser.parseArray(data.sectionItems);
    }
}
//# sourceMappingURL=GuideCollapsibleSectionEntry.js.map