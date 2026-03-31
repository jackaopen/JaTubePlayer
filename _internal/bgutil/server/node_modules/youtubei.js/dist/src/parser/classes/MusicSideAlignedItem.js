import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class MusicSideAlignedItem extends YTNode {
    static type = 'MusicSideAlignedItem';
    start_items;
    end_items;
    constructor(data) {
        super();
        if (Reflect.has(data, 'startItems')) {
            this.start_items = Parser.parseArray(data.startItems);
        }
        if (Reflect.has(data, 'endItems')) {
            this.end_items = Parser.parseArray(data.endItems);
        }
    }
}
//# sourceMappingURL=MusicSideAlignedItem.js.map