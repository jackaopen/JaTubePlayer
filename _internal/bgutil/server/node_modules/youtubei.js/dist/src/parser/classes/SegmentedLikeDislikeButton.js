import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import ToggleButton from './ToggleButton.js';
export default class SegmentedLikeDislikeButton extends YTNode {
    static type = 'SegmentedLikeDislikeButton';
    like_button;
    dislike_button;
    constructor(data) {
        super();
        this.like_button = Parser.parseItem(data.likeButton, [ToggleButton, Button]);
        this.dislike_button = Parser.parseItem(data.dislikeButton, [ToggleButton, Button]);
    }
}
//# sourceMappingURL=SegmentedLikeDislikeButton.js.map