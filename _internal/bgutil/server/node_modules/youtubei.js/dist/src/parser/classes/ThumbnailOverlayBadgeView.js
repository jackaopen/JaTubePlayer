import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ThumbnailBadgeView from './ThumbnailBadgeView.js';
export default class ThumbnailOverlayBadgeView extends YTNode {
    static type = 'ThumbnailOverlayBadgeView';
    badges;
    position;
    constructor(data) {
        super();
        this.badges = Parser.parseArray(data.thumbnailBadges, ThumbnailBadgeView);
        this.position = data.position;
    }
}
//# sourceMappingURL=ThumbnailOverlayBadgeView.js.map