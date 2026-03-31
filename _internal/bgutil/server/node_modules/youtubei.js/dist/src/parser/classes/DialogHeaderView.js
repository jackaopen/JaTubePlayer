import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class DialogHeaderView extends YTNode {
    static type = 'DialogHeaderView';
    headline;
    constructor(data) {
        super();
        this.headline = Text.fromAttributed(data.headline);
    }
}
//# sourceMappingURL=DialogHeaderView.js.map