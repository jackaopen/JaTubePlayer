import MetadataBadge from './MetadataBadge.js';
import Thumbnail from './misc/Thumbnail.js';
export default class LiveChatAuthorBadge extends MetadataBadge {
    static type = 'LiveChatAuthorBadge';
    custom_thumbnail;
    constructor(data) {
        super(data);
        this.custom_thumbnail = Thumbnail.fromResponse(data.customThumbnail);
    }
}
//# sourceMappingURL=LiveChatAuthorBadge.js.map