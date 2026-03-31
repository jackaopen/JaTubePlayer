import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ThumbnailBadgeView from './ThumbnailBadgeView.js';
import ThumbnailOverlayProgressBarView from './ThumbnailOverlayProgressBarView.js';
export default class ThumbnailBottomOverlayView extends YTNode {
    static type = 'ThumbnailBottomOverlayView';
    progress_bar;
    badges;
    constructor(data) {
        super();
        this.progress_bar = Parser.parseItem(data.progressBar, ThumbnailOverlayProgressBarView);
        this.badges = Parser.parseArray(data.badges, ThumbnailBadgeView);
    }
}
//# sourceMappingURL=ThumbnailBottomOverlayView.js.map