import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class StartAt extends YTNode {
    static type = 'StartAt';
    start_at_option_label;
    constructor(data) {
        super();
        this.start_at_option_label = new Text(data.startAtOptionLabel);
    }
}
//# sourceMappingURL=StartAt.js.map