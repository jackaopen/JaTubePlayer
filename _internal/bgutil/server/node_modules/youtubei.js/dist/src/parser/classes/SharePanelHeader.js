import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class SharePanelHeader extends YTNode {
    static type = 'SharePanelHeader';
    title;
    constructor(data) {
        super();
        this.title = Parser.parseItem(data.title);
    }
}
//# sourceMappingURL=SharePanelHeader.js.map