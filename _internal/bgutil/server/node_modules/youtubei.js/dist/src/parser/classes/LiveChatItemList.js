import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
export default class LiveChatItemList extends YTNode {
    static type = 'LiveChatItemList';
    max_items_to_display;
    more_comments_below_button;
    constructor(data) {
        super();
        this.max_items_to_display = data.maxItemsToDisplay;
        this.more_comments_below_button = Parser.parseItem(data.moreCommentsBelowButton, Button);
    }
}
//# sourceMappingURL=LiveChatItemList.js.map