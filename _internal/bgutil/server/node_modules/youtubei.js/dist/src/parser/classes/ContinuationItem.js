import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ContinuationItem extends YTNode {
    static type = 'ContinuationItem';
    trigger;
    button;
    endpoint;
    constructor(data) {
        super();
        this.trigger = data.trigger;
        if (Reflect.has(data, 'button')) {
            this.button = Parser.parseItem(data.button, Button);
        }
        this.endpoint = new NavigationEndpoint(data.continuationEndpoint);
    }
}
//# sourceMappingURL=ContinuationItem.js.map