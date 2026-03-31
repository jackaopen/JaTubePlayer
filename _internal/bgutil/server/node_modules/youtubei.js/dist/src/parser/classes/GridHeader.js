import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class GridHeader extends YTNode {
    static type = 'GridHeader';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=GridHeader.js.map