import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import DropdownItem from './DropdownItem.js';
export default class Dropdown extends YTNode {
    static type = 'Dropdown';
    label;
    entries;
    constructor(data) {
        super();
        this.label = data.label || '';
        this.entries = Parser.parseArray(data.entries, DropdownItem);
    }
}
//# sourceMappingURL=Dropdown.js.map