import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class TranscriptSegment extends YTNode {
    static type = 'TranscriptSegment';
    start_ms;
    end_ms;
    snippet;
    start_time_text;
    target_id;
    constructor(data) {
        super();
        this.start_ms = data.startMs;
        this.end_ms = data.endMs;
        this.snippet = new Text(data.snippet);
        this.start_time_text = new Text(data.startTimeText);
        this.target_id = data.targetId;
    }
}
//# sourceMappingURL=TranscriptSegment.js.map