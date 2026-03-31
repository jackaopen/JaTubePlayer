import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class MusicEditablePlaylistDetailHeader extends YTNode {
    static type = 'MusicEditablePlaylistDetailHeader';
    header;
    edit_header;
    playlist_id;
    constructor(data) {
        super();
        this.header = Parser.parseItem(data.header);
        this.edit_header = Parser.parseItem(data.editHeader);
        this.playlist_id = data.playlistId;
    }
}
//# sourceMappingURL=MusicEditablePlaylistDetailHeader.js.map