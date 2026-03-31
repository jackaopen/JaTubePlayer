import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class SharePanelTitleV15 extends YTNode {
    static type = 'SharePanelTitleV15';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=SharePanelTitleV15.js.map