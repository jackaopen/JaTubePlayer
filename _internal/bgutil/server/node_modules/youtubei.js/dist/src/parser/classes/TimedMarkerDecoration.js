import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class TimedMarkerDecoration extends YTNode {
    static type = 'TimedMarkerDecoration';
    visible_time_range_start_millis;
    visible_time_range_end_millis;
    decoration_time_millis;
    label;
    icon;
    constructor(data) {
        super();
        this.visible_time_range_start_millis = data.visibleTimeRangeStartMillis;
        this.visible_time_range_end_millis = data.visibleTimeRangeEndMillis;
        this.decoration_time_millis = data.decorationTimeMillis;
        this.label = new Text(data.label);
        this.icon = data.icon;
    }
}
//# sourceMappingURL=TimedMarkerDecoration.js.map