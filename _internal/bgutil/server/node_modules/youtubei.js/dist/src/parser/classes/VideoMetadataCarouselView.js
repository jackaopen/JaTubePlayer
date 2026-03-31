import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import CarouselItemView from './CarouselItemView.js';
import CarouselTitleView from './CarouselTitleView.js';
export default class VideoMetadataCarouselView extends YTNode {
    static type = 'VideoMetadataCarouselView';
    carousel_titles;
    carousel_items;
    constructor(data) {
        super();
        this.carousel_titles = Parser.parse(data.carouselTitles, true, CarouselTitleView);
        this.carousel_items = Parser.parse(data.carouselItems, true, CarouselItemView);
    }
}
//# sourceMappingURL=VideoMetadataCarouselView.js.map