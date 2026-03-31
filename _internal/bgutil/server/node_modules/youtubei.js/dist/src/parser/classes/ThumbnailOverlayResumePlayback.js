import { YTNode } from '../helpers.js';
export default class ThumbnailOverlayResumePlayback extends YTNode {
    static type = 'ThumbnailOverlayResumePlayback';
    percent_duration_watched;
    constructor(data) {
        super();
        this.percent_duration_watched = data.percentDurationWatched;
    }
}
//# sourceMappingURL=ThumbnailOverlayResumePlayback.js.map