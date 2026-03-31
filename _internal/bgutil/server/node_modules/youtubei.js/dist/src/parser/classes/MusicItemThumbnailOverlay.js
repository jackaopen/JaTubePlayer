import { Parser } from '../index.js';
import MusicPlayButton from './MusicPlayButton.js';
import { YTNode } from '../helpers.js';
export default class MusicItemThumbnailOverlay extends YTNode {
    static type = 'MusicItemThumbnailOverlay';
    content;
    content_position;
    display_style;
    constructor(data) {
        super();
        this.content = Parser.parseItem(data.content, MusicPlayButton);
        this.content_position = data.contentPosition;
        this.display_style = data.displayStyle;
    }
}
//# sourceMappingURL=MusicItemThumbnailOverlay.js.map