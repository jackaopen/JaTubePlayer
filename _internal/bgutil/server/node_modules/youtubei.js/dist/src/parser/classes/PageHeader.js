import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import PageHeaderView from './PageHeaderView.js';
export default class PageHeader extends YTNode {
    static type = 'PageHeader';
    page_title;
    content;
    constructor(data) {
        super();
        this.page_title = data.pageTitle;
        this.content = Parser.parseItem(data.content, PageHeaderView);
    }
}
//# sourceMappingURL=PageHeader.js.map