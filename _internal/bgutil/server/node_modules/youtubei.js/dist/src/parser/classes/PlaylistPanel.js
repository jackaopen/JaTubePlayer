import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import AutomixPreviewVideo from './AutomixPreviewVideo.js';
import PlaylistPanelVideo from './PlaylistPanelVideo.js';
import PlaylistPanelVideoWrapper from './PlaylistPanelVideoWrapper.js';
import Text from './misc/Text.js';
export default class PlaylistPanel extends YTNode {
    static type = 'PlaylistPanel';
    title;
    title_text;
    contents;
    playlist_id;
    is_infinite;
    continuation;
    is_editable;
    preview_description;
    num_items_to_show;
    constructor(data) {
        super();
        this.title = data.title;
        this.title_text = new Text(data.titleText);
        this.contents = Parser.parseArray(data.contents, [PlaylistPanelVideoWrapper, PlaylistPanelVideo, AutomixPreviewVideo]);
        this.playlist_id = data.playlistId;
        this.is_infinite = data.isInfinite;
        this.continuation = data.continuations?.[0]?.nextRadioContinuationData?.continuation || data.continuations?.[0]?.nextContinuationData?.continuation;
        this.is_editable = data.isEditable;
        this.preview_description = data.previewDescription;
        this.num_items_to_show = data.numItemsToShow;
    }
}
//# sourceMappingURL=PlaylistPanel.js.map