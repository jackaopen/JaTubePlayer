import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class Notification extends YTNode {
    static type = 'Notification';
    thumbnails;
    video_thumbnails;
    short_message;
    sent_time;
    notification_id;
    endpoint;
    record_click_endpoint;
    menu;
    read;
    constructor(data) {
        super();
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.video_thumbnails = Thumbnail.fromResponse(data.videoThumbnail);
        this.short_message = new Text(data.shortMessage);
        this.sent_time = new Text(data.sentTimeText);
        this.notification_id = data.notificationId;
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.record_click_endpoint = new NavigationEndpoint(data.recordClickEndpoint);
        this.menu = Parser.parseItem(data.contextualMenu);
        this.read = data.read;
    }
}
//# sourceMappingURL=Notification.js.map