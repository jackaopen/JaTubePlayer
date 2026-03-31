import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
export default class UpdateViewershipAction extends YTNode {
    static type = 'UpdateViewershipAction';
    view_count;
    extra_short_view_count;
    original_view_count;
    unlabeled_view_count_value;
    is_live;
    constructor(data) {
        super();
        const view_count_renderer = data.viewCount.videoViewCountRenderer;
        this.view_count = new Text(view_count_renderer.viewCount);
        this.extra_short_view_count = new Text(view_count_renderer.extraShortViewCount);
        this.original_view_count = parseInt(view_count_renderer.originalViewCount);
        this.unlabeled_view_count_value = new Text(view_count_renderer.unlabeledViewCountValue);
        this.is_live = view_count_renderer.isLive;
    }
}
//# sourceMappingURL=UpdateViewershipAction.js.map