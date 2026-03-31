import { YTNode } from '../../../helpers.js';
import { Parser } from '../../../index.js';
import Button from '../../Button.js';
import Text from '../../misc/Text.js';
import Thumbnail from '../../misc/Thumbnail.js';
export default class LiveChatBannerPoll extends YTNode {
    static type = 'LiveChatBannerPoll';
    poll_question;
    author_photo;
    choices;
    collapsed_state_entity_key;
    live_chat_poll_state_entity_key;
    context_menu_button;
    constructor(data) {
        super();
        this.poll_question = new Text(data.pollQuestion);
        this.author_photo = Thumbnail.fromResponse(data.authorPhoto);
        this.choices = data.pollChoices.map((choice) => ({
            option_id: choice.pollOptionId,
            text: new Text(choice.text).toString() // XXX: This toString should probably not be used here.
        }));
        this.collapsed_state_entity_key = data.collapsedStateEntityKey;
        this.live_chat_poll_state_entity_key = data.liveChatPollStateEntityKey;
        this.context_menu_button = Parser.parseItem(data.contextMenuButton, Button);
    }
}
//# sourceMappingURL=LiveChatBannerPoll.js.map