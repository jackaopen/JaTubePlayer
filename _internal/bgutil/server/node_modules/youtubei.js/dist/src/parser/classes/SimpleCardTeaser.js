import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class SimpleCardTeaser extends YTNode {
    static type = 'SimpleCardTeaser';
    message;
    prominent; // @TODO: or string?
    constructor(data) {
        super();
        this.message = new Text(data.message);
        this.prominent = data.prominent;
    }
}
//# sourceMappingURL=SimpleCardTeaser.js.map