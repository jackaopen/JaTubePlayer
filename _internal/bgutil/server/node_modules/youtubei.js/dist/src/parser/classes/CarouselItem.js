import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
export default class CarouselItem extends YTNode {
    static type = 'CarouselItem';
    items;
    background_color;
    layout_style;
    pagination_thumbnails;
    paginator_alignment;
    constructor(data) {
        super();
        this.items = Parser.parseArray(data.carouselItems);
        this.background_color = data.backgroundColor;
        this.layout_style = data.layoutStyle;
        this.pagination_thumbnails = Thumbnail.fromResponse(data.paginationThumbnails);
        this.paginator_alignment = data.paginatorAlignment;
    }
    // XXX: For consistency.
    get contents() {
        return this.items;
    }
}
//# sourceMappingURL=CarouselItem.js.map