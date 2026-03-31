import { Parser } from '../index.js';
import Text from './misc/Text.js';
import Button from './Button.js';
import { YTNode } from '../helpers.js';
export default class ConfirmDialog extends YTNode {
    static type = 'ConfirmDialog';
    title;
    confirm_button;
    cancel_button;
    dialog_messages;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.confirm_button = Parser.parseItem(data.confirmButton, Button);
        this.cancel_button = Parser.parseItem(data.cancelButton, Button);
        this.dialog_messages = data.dialogMessages.map((txt) => new Text(txt));
    }
}
//# sourceMappingURL=ConfirmDialog.js.map