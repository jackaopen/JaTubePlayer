import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
/**
 * Not a real renderer but we treat it as one to keep things organized.
 */
export default class AccountItem extends YTNode {
    static type = 'AccountItem';
    account_name;
    account_photo;
    is_selected;
    is_disabled;
    has_channel;
    endpoint;
    account_byline;
    channel_handle;
    constructor(data) {
        super();
        this.account_name = new Text(data.accountName);
        this.account_photo = Thumbnail.fromResponse(data.accountPhoto);
        this.is_selected = !!data.isSelected;
        this.is_disabled = !!data.isDisabled;
        this.has_channel = !!data.hasChannel;
        this.endpoint = new NavigationEndpoint(data.serviceEndpoint);
        this.account_byline = new Text(data.accountByline);
        this.channel_handle = new Text(data.channelHandle);
    }
}
//# sourceMappingURL=AccountItem.js.map