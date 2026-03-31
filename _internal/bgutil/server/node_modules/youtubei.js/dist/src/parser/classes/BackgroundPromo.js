import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Text from './misc/Text.js';
import Button from './Button.js';
import ButtonView from './ButtonView.js';
export default class BackgroundPromo extends YTNode {
    static type = 'BackgroundPromo';
    body_text;
    cta_button;
    icon_type;
    title;
    constructor(data) {
        super();
        this.body_text = new Text(data.bodyText);
        this.cta_button = Parser.parseItem(data.ctaButton, [Button, ButtonView]);
        if (Reflect.has(data, 'icon'))
            this.icon_type = data.icon.iconType;
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=BackgroundPromo.js.map