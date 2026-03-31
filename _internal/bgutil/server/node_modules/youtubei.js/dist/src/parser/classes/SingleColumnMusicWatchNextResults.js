import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class SingleColumnMusicWatchNextResults extends YTNode {
    static type = 'SingleColumnMusicWatchNextResults';
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parse(data);
    }
}
//# sourceMappingURL=SingleColumnMusicWatchNextResults.js.map