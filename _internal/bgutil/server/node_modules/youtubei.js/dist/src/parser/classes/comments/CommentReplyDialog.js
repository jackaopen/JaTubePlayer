import { Parser } from '../../index.js';
import Button from '../Button.js';
import Text from '../misc/Text.js';
import Thumbnail from '../misc/Thumbnail.js';
import { YTNode } from '../../helpers.js';
export default class CommentReplyDialog extends YTNode {
    static type = 'CommentReplyDialog';
    reply_button;
    cancel_button;
    author_thumbnail;
    placeholder;
    error_message;
    constructor(data) {
        super();
        this.reply_button = Parser.parseItem(data.replyButton, Button);
        this.cancel_button = Parser.parseItem(data.cancelButton, Button);
        this.author_thumbnail = Thumbnail.fromResponse(data.authorThumbnail);
        this.placeholder = new Text(data.placeholderText);
        this.error_message = new Text(data.errorMessage);
    }
}
//# sourceMappingURL=CommentReplyDialog.js.map