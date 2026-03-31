import { Parser } from '../index.js';
import { YTNode, observe } from '../helpers.js';
import PlaylistPanelVideo from './PlaylistPanelVideo.js';
export default class PlaylistPanelVideoWrapper extends YTNode {
    static type = 'PlaylistPanelVideoWrapper';
    primary;
    counterpart;
    constructor(data) {
        super();
        this.primary = Parser.parseItem(data.primaryRenderer, PlaylistPanelVideo);
        if (Reflect.has(data, 'counterpart')) {
            this.counterpart = observe(data.counterpart.map((item) => Parser.parseItem(item.counterpartRenderer, PlaylistPanelVideo)) || []);
        }
    }
}
//# sourceMappingURL=PlaylistPanelVideoWrapper.js.map