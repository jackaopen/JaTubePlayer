import { YTNode } from '../helpers.js';
export default class EmojiPickerCategoryButton extends YTNode {
    static type = 'EmojiPickerCategoryButton';
    category_id;
    icon_type;
    tooltip;
    constructor(data) {
        super();
        this.category_id = data.categoryId;
        if (Reflect.has(data, 'icon')) {
            this.icon_type = data.icon?.iconType;
        }
        this.tooltip = data.tooltip;
    }
}
//# sourceMappingURL=EmojiPickerCategoryButton.js.map