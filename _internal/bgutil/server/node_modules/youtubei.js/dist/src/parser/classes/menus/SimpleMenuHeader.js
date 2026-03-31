import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import Button from '../Button.js';
import Text from '../misc/Text.js';
export default class SimpleMenuHeader extends YTNode {
    static type = 'SimpleMenuHeader';
    title;
    buttons;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.buttons = Parser.parseArray(data.buttons, Button);
    }
}
//# sourceMappingURL=SimpleMenuHeader.js.map