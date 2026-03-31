import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class FancyDismissibleDialog extends YTNode {
    static type = 'FancyDismissibleDialog';
    dialog_message;
    confirm_label;
    constructor(data) {
        super();
        this.dialog_message = new Text(data.dialogMessage);
        this.confirm_label = new Text(data.confirmLabel);
    }
}
//# sourceMappingURL=FancyDismissibleDialog.js.map