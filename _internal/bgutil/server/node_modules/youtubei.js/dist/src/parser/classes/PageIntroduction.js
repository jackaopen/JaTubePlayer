import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class PageIntroduction extends YTNode {
    static type = 'PageIntroduction';
    header_text;
    body_text;
    page_title;
    header_icon_type;
    constructor(data) {
        super();
        this.header_text = new Text(data.headerText).toString();
        this.body_text = new Text(data.bodyText).toString();
        this.page_title = new Text(data.pageTitle).toString();
        this.header_icon_type = data.headerIcon.iconType;
    }
}
//# sourceMappingURL=PageIntroduction.js.map