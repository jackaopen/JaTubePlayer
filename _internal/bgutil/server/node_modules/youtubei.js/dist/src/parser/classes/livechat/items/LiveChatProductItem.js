import { Parser } from '../../../index.js';
import { YTNode } from '../../../helpers.js';
import Text from '../../misc/Text.js';
import Thumbnail from '../../misc/Thumbnail.js';
import NavigationEndpoint from '../../NavigationEndpoint.js';
export default class LiveChatProductItem extends YTNode {
    static type = 'LiveChatProductItem';
    title;
    accessibility_title;
    thumbnail;
    price;
    vendor_name;
    from_vendor_text;
    information_button;
    endpoint;
    creator_message;
    creator_name;
    author_photo;
    information_dialog;
    is_verified;
    creator_custom_message;
    constructor(data) {
        super();
        this.title = data.title;
        this.accessibility_title = data.accessibilityTitle;
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
        this.price = data.price;
        this.vendor_name = data.vendorName;
        this.from_vendor_text = data.fromVendorText;
        this.information_button = Parser.parseItem(data.informationButton);
        this.endpoint = new NavigationEndpoint(data.onClickCommand);
        this.creator_message = data.creatorMessage;
        this.creator_name = data.creatorName;
        this.author_photo = Thumbnail.fromResponse(data.authorPhoto);
        this.information_dialog = Parser.parseItem(data.informationDialog);
        this.is_verified = data.isVerified;
        this.creator_custom_message = new Text(data.creatorCustomMessage);
    }
}
//# sourceMappingURL=LiveChatProductItem.js.map