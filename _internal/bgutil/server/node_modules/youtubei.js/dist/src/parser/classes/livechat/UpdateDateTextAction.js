import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
export default class UpdateDateTextAction extends YTNode {
    static type = 'UpdateDateTextAction';
    date_text;
    constructor(data) {
        super();
        this.date_text = new Text(data.dateText).toString();
    }
}
//# sourceMappingURL=UpdateDateTextAction.js.map