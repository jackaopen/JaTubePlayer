import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class TranscriptSectionHeader extends YTNode {
    static type = 'TranscriptSectionHeader';
    start_ms;
    end_ms;
    snippet;
    constructor(data) {
        super();
        this.start_ms = data.startMs;
        this.end_ms = data.endMs;
        this.snippet = new Text(data.snippet);
    }
}
//# sourceMappingURL=TranscriptSectionHeader.js.map