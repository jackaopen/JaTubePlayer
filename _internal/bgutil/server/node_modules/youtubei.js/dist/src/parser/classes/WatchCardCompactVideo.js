import { timeToSeconds } from '../../utils/Utils.js';
import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class WatchCardCompactVideo extends YTNode {
    static type = 'WatchCardCompactVideo';
    title;
    subtitle;
    duration;
    style;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.subtitle = new Text(data.subtitle);
        this.duration = {
            text: new Text(data.lengthText).toString(),
            seconds: timeToSeconds(data.lengthText.simpleText)
        };
        this.style = data.style;
    }
}
//# sourceMappingURL=WatchCardCompactVideo.js.map