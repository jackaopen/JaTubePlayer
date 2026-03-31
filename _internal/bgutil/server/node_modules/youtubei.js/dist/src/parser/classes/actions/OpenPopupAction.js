import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class OpenPopupAction extends YTNode {
    static type = 'OpenPopupAction';
    popup;
    popup_type;
    constructor(data) {
        super();
        this.popup = Parser.parseItem(data.popup);
        this.popup_type = data.popupType;
    }
}
//# sourceMappingURL=OpenPopupAction.js.map