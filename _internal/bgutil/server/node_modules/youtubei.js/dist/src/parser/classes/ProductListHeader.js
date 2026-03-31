import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class ProductListHeader extends YTNode {
    static type = 'ProductListHeader';
    title;
    suppress_padding_disclaimer;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.suppress_padding_disclaimer = !!data.suppressPaddingDisclaimer;
    }
}
//# sourceMappingURL=ProductListHeader.js.map