import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import MusicResponsiveListItem from './MusicResponsiveListItem.js';
import ContinuationItem from './ContinuationItem.js';
export default class MusicPlaylistShelf extends YTNode {
    static type = 'MusicPlaylistShelf';
    playlist_id;
    contents;
    collapsed_item_count;
    continuation;
    constructor(data) {
        super();
        this.playlist_id = data.playlistId;
        this.contents = Parser.parseArray(data.contents, [MusicResponsiveListItem, ContinuationItem]);
        this.collapsed_item_count = data.collapsedItemCount;
        this.continuation = data.continuations?.[0]?.nextContinuationData?.continuation || null;
    }
}
//# sourceMappingURL=MusicPlaylistShelf.js.map