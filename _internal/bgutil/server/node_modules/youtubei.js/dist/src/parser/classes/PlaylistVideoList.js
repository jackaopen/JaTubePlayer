import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class PlaylistVideoList extends YTNode {
    static type = 'PlaylistVideoList';
    id;
    is_editable;
    can_reorder;
    videos;
    constructor(data) {
        super();
        this.id = data.playlistId;
        this.is_editable = data.isEditable;
        this.can_reorder = data.canReorder;
        this.videos = Parser.parseArray(data.contents);
    }
}
//# sourceMappingURL=PlaylistVideoList.js.map