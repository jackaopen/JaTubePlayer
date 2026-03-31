import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Message from './Message.js';
export default class ConversationBar extends YTNode {
    static type = 'ConversationBar';
    availability_message;
    constructor(data) {
        super();
        this.availability_message = Parser.parseItem(data.availabilityMessage, Message);
    }
}
//# sourceMappingURL=ConversationBar.js.map