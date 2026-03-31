import { YTNode } from '../helpers.js';
export default class ThumbnailOverlayProgressBarView extends YTNode {
    static type = 'ThumbnailOverlayProgressBarView';
    start_percent;
    constructor(data) {
        super();
        this.start_percent = data.startPercent;
    }
}
//# sourceMappingURL=ThumbnailOverlayProgressBarView.js.map