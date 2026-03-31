import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import Text from './misc/Text.js';
export default class LiveChatDialog extends YTNode {
    static type = 'LiveChatDialog';
    confirm_button;
    dialog_messages;
    constructor(data) {
        super();
        this.confirm_button = Parser.parseItem(data.confirmButton, Button);
        this.dialog_messages = data.dialogMessages.map((el) => new Text(el));
    }
}
//# sourceMappingURL=LiveChatDialog.js.map