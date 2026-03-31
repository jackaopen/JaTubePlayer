import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import TextCarouselItemView from './TextCarouselItemView.js';
export default class CarouselItemView extends YTNode {
    static type = 'CarouselItemView';
    item_type;
    carousel_item;
    constructor(data) {
        super();
        this.item_type = data.itemType;
        this.carousel_item = Parser.parseItem(data.carouselItem, TextCarouselItemView);
    }
}
//# sourceMappingURL=CarouselItemView.js.map