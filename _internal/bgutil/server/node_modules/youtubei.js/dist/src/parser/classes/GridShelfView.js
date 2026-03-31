import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ButtonView from './ButtonView.js';
export default class GridShelfView extends YTNode {
    static type = 'GridShelfView';
    contents;
    header;
    content_aspect_ratio;
    enable_vertical_expansion;
    show_more_button;
    show_less_button;
    min_collapsed_item_count;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents);
        this.header = Parser.parseItem(data.header);
        this.content_aspect_ratio = data.contentAspectRatio;
        this.enable_vertical_expansion = data.enableVerticalExpansion;
        this.show_more_button = Parser.parseItem(data.showMoreButton, ButtonView);
        this.show_less_button = Parser.parseItem(data.showLessButton, ButtonView);
        this.min_collapsed_item_count = data.minCollapsedItemCount;
    }
}
//# sourceMappingURL=GridShelfView.js.map