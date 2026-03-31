import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class PlaylistSidebarSecondaryInfo extends YTNode {
    static type = 'PlaylistSidebarSecondaryInfo';
    owner;
    button;
    constructor(data) {
        super();
        this.owner = Parser.parseItem(data.videoOwner);
        this.button = Parser.parseItem(data.button);
    }
}
//# sourceMappingURL=PlaylistSidebarSecondaryInfo.js.map