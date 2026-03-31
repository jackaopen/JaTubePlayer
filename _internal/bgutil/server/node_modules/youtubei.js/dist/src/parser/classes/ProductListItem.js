import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import { Text, Thumbnail } from '../misc.js';
import Button from './Button.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ProductListItem extends YTNode {
    static type = 'ProductListItem';
    title;
    accessibility_title;
    thumbnail;
    price;
    endpoint;
    merchant_name;
    stay_in_app;
    view_button;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.accessibility_title = data.accessibilityTitle;
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
        this.price = data.price;
        this.endpoint = new NavigationEndpoint(data.onClickCommand);
        this.merchant_name = data.merchantName;
        this.stay_in_app = !!data.stayInApp;
        this.view_button = Parser.parseItem(data.viewButton, Button);
    }
}
//# sourceMappingURL=ProductListItem.js.map