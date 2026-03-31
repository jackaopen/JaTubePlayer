import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class ShowLiveChatDialogAction extends YTNode {
    static type = 'ShowLiveChatDialogAction';
    dialog;
    constructor(data) {
        super();
        this.dialog = Parser.parseItem(data.dialog);
    }
}
//# sourceMappingURL=ShowLiveChatDialogAction.js.map