import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Text from './misc/Text.js';
import Form from './Form.js';
import Button from './Button.js';
export default class FormPopup extends YTNode {
    static type = 'FormPopup';
    title;
    form;
    buttons;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.form = Parser.parseItem(data.form, Form);
        this.buttons = Parser.parseArray(data.buttons, Button);
    }
}
//# sourceMappingURL=FormPopup.js.map