import { YTNode } from '../helpers.js';
export default class OpenOnePickAddVideoModalCommand extends YTNode {
    static type = 'OpenOnePickAddVideoModalCommand';
    list_id;
    modal_title;
    select_button_label;
    constructor(data) {
        super();
        this.list_id = data.listId;
        this.modal_title = data.modalTitle;
        this.select_button_label = data.selectButtonLabel;
    }
}
//# sourceMappingURL=OpenOnePickAddVideoModalCommand.js.map