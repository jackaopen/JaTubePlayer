import { YTNode } from '../../helpers.js';
import Text from '../misc/Text.js';
import { Parser } from '../../index.js';
export default class MobileTopbar extends YTNode {
    static type = 'MobileTopbar';
    placeholder_text;
    buttons;
    logo_type;
    constructor(data) {
        super();
        this.placeholder_text = new Text(data.placeholderText);
        this.buttons = Parser.parseArray(data.buttons);
        if (Reflect.has(data, 'logo') && Reflect.has(data.logo, 'iconType'))
            this.logo_type = data.logo.iconType;
    }
}
//# sourceMappingURL=MobileTopbar.js.map