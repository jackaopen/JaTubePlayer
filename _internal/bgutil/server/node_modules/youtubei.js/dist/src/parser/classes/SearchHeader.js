import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import ChipCloud from './ChipCloud.js';
export default class SearchHeader extends YTNode {
    static type = 'SearchHeader';
    chip_bar;
    search_filter_button;
    constructor(data) {
        super();
        this.chip_bar = Parser.parseItem(data.chipBar, ChipCloud);
        this.search_filter_button = Parser.parseItem(data.searchFilterButton, Button);
    }
}
//# sourceMappingURL=SearchHeader.js.map