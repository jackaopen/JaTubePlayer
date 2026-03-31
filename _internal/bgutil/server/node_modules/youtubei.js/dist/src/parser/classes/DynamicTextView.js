import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class DynamicTextView extends YTNode {
    static type = 'DynamicTextView';
    text;
    max_lines;
    constructor(data) {
        super();
        this.text = Text.fromAttributed(data.text);
        this.max_lines = parseInt(data.maxLines);
    }
}
//# sourceMappingURL=DynamicTextView.js.map