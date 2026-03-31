import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class ExpandableVideoDescriptionBody extends YTNode {
    static type = 'ExpandableVideoDescriptionBody';
    show_more_text;
    show_less_text;
    attributed_description_body_text;
    constructor(data) {
        super();
        this.show_more_text = new Text(data.showMoreText);
        this.show_less_text = new Text(data.showLessText);
        if (Reflect.has(data, 'attributedDescriptionBodyText')) {
            this.attributed_description_body_text = Text.fromAttributed(data.attributedDescriptionBodyText);
        }
    }
}
//# sourceMappingURL=ExpandableVideoDescriptionBody.js.map