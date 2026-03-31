import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import LiveChatParticipant from './LiveChatParticipant.js';
import Text from './misc/Text.js';
export default class LiveChatParticipantsList extends YTNode {
    static type = 'LiveChatParticipantsList';
    title;
    participants;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.participants = Parser.parseArray(data.participants, LiveChatParticipant);
    }
}
//# sourceMappingURL=LiveChatParticipantsList.js.map