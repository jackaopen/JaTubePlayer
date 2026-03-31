import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class Factoid extends YTNode {
    static type = 'Factoid';
    label;
    value;
    accessibility_text;
    constructor(data) {
        super();
        this.label = new Text(data.label);
        this.value = new Text(data.value);
        this.accessibility_text = data.accessibilityText;
    }
}
//# sourceMappingURL=Factoid.js.map