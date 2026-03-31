import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class SimpleTextSection extends YTNode {
    static type = 'SimpleTextSection';
    lines;
    style;
    constructor(data) {
        super();
        this.lines = data.lines.map((line) => new Text(line));
        this.style = data.layoutStyle;
    }
}
//# sourceMappingURL=SimpleTextSection.js.map