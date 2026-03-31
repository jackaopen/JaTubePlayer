import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import ContinuationItem from '../ContinuationItem.js';
import Message from '../Message.js';
import Notification from '../Notification.js';
import Text from '../misc/Text.js';
export default class MultiPageMenuNotificationSection extends YTNode {
    static type = 'MultiPageMenuNotificationSection';
    notification_section_title;
    items;
    constructor(data) {
        super();
        if ('notificationSectionTitle' in data) {
            this.notification_section_title = new Text(data.notificationSectionTitle);
        }
        this.items = Parser.parseArray(data.items, [Notification, Message, ContinuationItem]);
    }
    // XXX: Alias for consistency.
    get contents() {
        return this.items;
    }
}
//# sourceMappingURL=MultiPageMenuNotificationSection.js.map