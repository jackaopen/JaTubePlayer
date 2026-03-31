import { YTNode } from '../../../helpers.js';
import { Parser } from '../../../index.js';
import Button from '../../Button.js';
import Text from '../../misc/Text.js';
import Thumbnail from '../../misc/Thumbnail.js';
export default class PollHeader extends YTNode {
    static type = 'PollHeader';
    poll_question;
    thumbnails;
    metadata;
    live_chat_poll_type;
    context_menu_button;
    constructor(data) {
        super();
        this.poll_question = new Text(data.pollQuestion);
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.metadata = new Text(data.metadataText);
        this.live_chat_poll_type = data.liveChatPollType;
        this.context_menu_button = Parser.parseItem(data.contextMenuButton, Button);
    }
}
//# sourceMappingURL=PollHeader.js.map