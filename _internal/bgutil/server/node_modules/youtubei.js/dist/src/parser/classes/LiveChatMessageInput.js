import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class LiveChatMessageInput extends YTNode {
    static type = 'LiveChatMessageInput';
    author_name;
    author_photo;
    send_button;
    target_id;
    constructor(data) {
        super();
        this.author_name = new Text(data.authorName);
        this.author_photo = Thumbnail.fromResponse(data.authorPhoto);
        this.send_button = Parser.parseItem(data.sendButton, Button);
        this.target_id = data.targetId;
    }
}
//# sourceMappingURL=LiveChatMessageInput.js.map