import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import { Text } from '../misc.js';
import TranscriptSectionHeader from './TranscriptSectionHeader.js';
import TranscriptSegment from './TranscriptSegment.js';
export default class TranscriptSegmentList extends YTNode {
    static type = 'TranscriptSegmentList';
    initial_segments;
    no_result_label;
    retry_label;
    touch_captions_enabled;
    constructor(data) {
        super();
        this.initial_segments = Parser.parseArray(data.initialSegments, [TranscriptSegment, TranscriptSectionHeader]);
        this.no_result_label = new Text(data.noResultLabel);
        this.retry_label = new Text(data.retryLabel);
        this.touch_captions_enabled = data.touchCaptionsEnabled;
    }
}
//# sourceMappingURL=TranscriptSegmentList.js.map