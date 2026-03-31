import { Text } from '../misc.js';
import { YTNode } from '../helpers.js';
export default class PlayerOverlayVideoDetails extends YTNode {
    static type = 'PlayerOverlayVideoDetails';
    title;
    subtitle;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.subtitle = new Text(data.subtitle);
    }
}
//# sourceMappingURL=PlayerOverlayVideoDetails.js.map