import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ButtonView from './ButtonView.js';
export default class CarouselTitleView extends YTNode {
    static type = 'CarouselTitleView';
    title;
    previous_button;
    next_button;
    constructor(data) {
        super();
        this.title = data.title;
        this.previous_button = Parser.parseItem(data.previousButton, ButtonView);
        this.next_button = Parser.parseItem(data.nextButton, ButtonView);
    }
}
//# sourceMappingURL=CarouselTitleView.js.map