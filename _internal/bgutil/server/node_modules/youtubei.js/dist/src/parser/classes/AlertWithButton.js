import Button from './Button.js';
import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class AlertWithButton extends YTNode {
    static type = 'AlertWithButton';
    text;
    alert_type;
    dismiss_button;
    constructor(data) {
        super();
        this.text = new Text(data.text);
        this.alert_type = data.type;
        this.dismiss_button = Parser.parseItem(data.dismissButton, Button);
    }
}
//# sourceMappingURL=AlertWithButton.js.map