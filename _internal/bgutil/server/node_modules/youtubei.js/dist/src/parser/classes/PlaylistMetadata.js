import { YTNode } from '../helpers.js';
export default class PlaylistMetadata extends YTNode {
    static type = 'PlaylistMetadata';
    title;
    description;
    constructor(data) {
        super();
        this.title = data.title;
        this.description = data.description || null;
        // XXX: Appindexing should be in microformat.
    }
}
//# sourceMappingURL=PlaylistMetadata.js.map