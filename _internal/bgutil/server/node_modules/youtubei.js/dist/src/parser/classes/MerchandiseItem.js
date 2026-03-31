import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class MerchandiseItem extends YTNode {
    static type = 'MerchandiseItem';
    title;
    description;
    thumbnails;
    price;
    vendor_name;
    button_text;
    button_accessibility_text;
    from_vendor_text;
    additional_fees_text;
    region_format;
    endpoint;
    constructor(data) {
        super();
        this.title = data.title;
        this.description = data.description;
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.price = data.price;
        this.vendor_name = data.vendorName;
        this.button_text = data.buttonText;
        this.button_accessibility_text = data.buttonAccessibilityText;
        this.from_vendor_text = data.fromVendorText;
        this.additional_fees_text = data.additionalFeesText;
        this.region_format = data.regionFormat;
        this.endpoint = new NavigationEndpoint(data.buttonCommand);
    }
}
//# sourceMappingURL=MerchandiseItem.js.map