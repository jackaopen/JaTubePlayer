import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class EmojiPickerCategory extends YTNode {
    static type = 'EmojiPickerCategory';
    category_id;
    title;
    emoji_ids;
    image_loading_lazy;
    category_type;
    constructor(data) {
        super();
        this.category_id = data.categoryId;
        this.title = new Text(data.title);
        this.emoji_ids = data.emojiIds;
        this.image_loading_lazy = !!data.imageLoadingLazy;
        this.category_type = data.categoryType;
    }
}
//# sourceMappingURL=EmojiPickerCategory.js.map