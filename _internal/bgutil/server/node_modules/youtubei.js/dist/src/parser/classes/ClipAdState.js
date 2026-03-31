import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ClipAdState extends YTNode {
    static type = 'ClipAdState';
    title;
    body;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.body = new Text(data.body);
    }
}
//# sourceMappingURL=ClipAdState.js.map