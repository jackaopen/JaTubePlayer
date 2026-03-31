import { YTNode } from '../../../helpers.js';
import { Parser } from '../../../index.js';
import LiveChatSponsorshipsHeader from './LiveChatSponsorshipsHeader.js';
export default class LiveChatSponsorshipsGiftPurchaseAnnouncement extends YTNode {
    static type = 'LiveChatSponsorshipsGiftPurchaseAnnouncement';
    id;
    timestamp_usec;
    author_external_channel_id;
    header;
    constructor(data) {
        super();
        this.id = data.id;
        this.timestamp_usec = data.timestampUsec;
        this.author_external_channel_id = data.authorExternalChannelId;
        this.header = Parser.parseItem(data.header, LiveChatSponsorshipsHeader);
    }
}
//# sourceMappingURL=LiveChatSponsorshipsGiftPurchaseAnnouncement.js.map