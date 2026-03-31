import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
export default class MultiPageMenu extends YTNode {
    static type = 'MultiPageMenu';
    header;
    sections;
    style;
    constructor(data) {
        super();
        this.header = Parser.parseItem(data.header);
        this.sections = Parser.parseArray(data.sections);
        this.style = data.style;
    }
}
//# sourceMappingURL=MultiPageMenu.js.map