import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class Message extends YTNode {
    static type = 'Message';
    text;
    constructor(data) {
        super();
        this.text = new Text(data.text);
    }
}
//# sourceMappingURL=Message.js.map