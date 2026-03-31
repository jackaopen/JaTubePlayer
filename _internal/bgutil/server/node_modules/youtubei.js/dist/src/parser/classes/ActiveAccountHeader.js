import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ActiveAccountHeader extends YTNode {
    static type = 'ActiveAccountHeader';
    account_name;
    account_photo;
    endpoint;
    manage_account_title;
    channel_handle;
    constructor(data) {
        super();
        this.account_name = new Text(data.accountName);
        this.account_photo = Thumbnail.fromResponse(data.accountPhoto);
        this.endpoint = new NavigationEndpoint(data.serviceEndpoint);
        this.manage_account_title = new Text(data.manageAccountTitle);
        this.channel_handle = new Text(data.channelHandle);
    }
}
//# sourceMappingURL=ActiveAccountHeader.js.map