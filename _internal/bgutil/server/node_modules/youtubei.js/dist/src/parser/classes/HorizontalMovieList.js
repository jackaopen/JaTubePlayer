import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import Button from './Button.js';
export default class HorizontalMovieList extends YTNode {
    static type = 'HorizontalMovieList';
    items;
    previous_button;
    next_button;
    constructor(data) {
        super();
        this.items = Parser.parseArray(data.items);
        this.previous_button = Parser.parseItem(data.previousButton, Button);
        this.next_button = Parser.parseItem(data.nextButton, Button);
    }
    // XXX: Alias for consistency.
    get contents() {
        return this.items;
    }
}
//# sourceMappingURL=HorizontalMovieList.js.map