import { Parser } from '../index.js';
import PlaylistPanel from './PlaylistPanel.js';
import { YTNode } from '../helpers.js';
export default class MusicQueue extends YTNode {
    static type = 'MusicQueue';
    content;
    constructor(data) {
        super();
        this.content = Parser.parseItem(data.content, PlaylistPanel);
    }
}
//# sourceMappingURL=MusicQueue.js.map