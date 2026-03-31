import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
export default class Chapter extends YTNode {
    static type = 'Chapter';
    title;
    time_range_start_millis;
    thumbnail;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.time_range_start_millis = data.timeRangeStartMillis;
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=Chapter.js.map