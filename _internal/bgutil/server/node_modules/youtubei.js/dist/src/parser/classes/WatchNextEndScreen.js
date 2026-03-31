import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import EndScreenPlaylist from './EndScreenPlaylist.js';
import EndScreenVideo from './EndScreenVideo.js';
import Text from './misc/Text.js';
export default class WatchNextEndScreen extends YTNode {
    static type = 'WatchNextEndScreen';
    results;
    title;
    constructor(data) {
        super();
        this.results = Parser.parseArray(data.results, [EndScreenVideo, EndScreenPlaylist]);
        this.title = new Text(data.title).toString();
    }
}
//# sourceMappingURL=WatchNextEndScreen.js.map