import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class LiveChatParticipant extends YTNode {
    static type = 'LiveChatParticipant';
    name;
    photo;
    badges;
    constructor(data) {
        super();
        this.name = new Text(data.authorName);
        this.photo = Thumbnail.fromResponse(data.authorPhoto);
        this.badges = Parser.parseArray(data.authorBadges);
    }
}
//# sourceMappingURL=LiveChatParticipant.js.map