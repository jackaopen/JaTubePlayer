import { Text } from '../misc.js';
import { YTNode } from '../helpers.js';
export default class VideoViewCount extends YTNode {
    static type = 'VideoViewCount';
    original_view_count;
    short_view_count;
    extra_short_view_count;
    view_count;
    constructor(data) {
        super();
        this.original_view_count = data.originalViewCount;
        this.short_view_count = new Text(data.shortViewCount);
        this.extra_short_view_count = new Text(data.extraShortViewCount);
        this.view_count = new Text(data.viewCount);
    }
}
//# sourceMappingURL=VideoViewCount.js.map