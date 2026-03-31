import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class CarouselHeader extends YTNode {
    static type = 'CarouselHeader';
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents);
    }
}
//# sourceMappingURL=CarouselHeader.js.map