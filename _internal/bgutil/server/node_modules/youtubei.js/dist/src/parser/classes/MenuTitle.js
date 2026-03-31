import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class MenuTitle extends YTNode {
    static type = 'MenuTitle';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=MenuTitle.js.map