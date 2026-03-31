import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class RichListHeader extends YTNode {
    static type = 'RichListHeader';
    title;
    subtitle;
    title_style;
    icon_type;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.subtitle = new Text(data.subtitle);
        if (Reflect.has(data, 'titleStyle')) {
            this.title_style = data.titleStyle.style;
        }
        if (Reflect.has(data, 'icon')) {
            this.icon_type = data.icon.iconType;
        }
    }
}
//# sourceMappingURL=RichListHeader.js.map