import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class EmojiPickerUpsellCategory extends YTNode {
    static type = 'EmojiPickerUpsellCategory';
    category_id;
    title;
    upsell;
    emoji_tooltip;
    endpoint;
    emoji_ids;
    constructor(data) {
        super();
        this.category_id = data.categoryId;
        this.title = new Text(data.title);
        this.upsell = new Text(data.upsell);
        this.emoji_tooltip = data.emojiTooltip;
        this.endpoint = new NavigationEndpoint(data.command);
        this.emoji_ids = data.emojiIds;
    }
}
//# sourceMappingURL=EmojiPickerUpsellCategory.js.map