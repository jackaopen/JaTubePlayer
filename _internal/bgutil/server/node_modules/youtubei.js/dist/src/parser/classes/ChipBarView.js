import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ChipView from './ChipView.js';
export default class ChipBarView extends YTNode {
    static type = 'ChipBarView';
    chips;
    constructor(data) {
        super();
        this.chips = Parser.parseArray(data.chips, ChipView);
    }
}
//# sourceMappingURL=ChipBarView.js.map