import Thumbnail from '../misc/Thumbnail.js';
import { YTNode } from '../../helpers.js';
export default class SponsorCommentBadge extends YTNode {
    static type = 'SponsorCommentBadge';
    custom_badge;
    tooltip;
    constructor(data) {
        super();
        this.custom_badge = Thumbnail.fromResponse(data.customBadge);
        this.tooltip = data.tooltip;
    }
}
//# sourceMappingURL=SponsorCommentBadge.js.map