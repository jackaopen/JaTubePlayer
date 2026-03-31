import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class NotificationAction extends YTNode {
    static type = 'NotificationAction';
    response_text;
    constructor(data) {
        super();
        this.response_text = new Text(data.responseText);
    }
}
//# sourceMappingURL=NotificationAction.js.map