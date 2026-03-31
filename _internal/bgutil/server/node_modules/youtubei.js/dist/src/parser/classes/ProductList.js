import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class ProductList extends YTNode {
    static type = 'ProductList';
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents);
    }
}
//# sourceMappingURL=ProductList.js.map