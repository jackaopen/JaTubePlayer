import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ThumbnailOverlayEndorsement extends YTNode {
    static type = 'ThumbnailOverlayEndorsement';
    text;
    constructor(data) {
        super();
        this.text = new Text(data.text).toString();
    }
}
//# sourceMappingURL=ThumbnailOverlayEndorsement.js.map