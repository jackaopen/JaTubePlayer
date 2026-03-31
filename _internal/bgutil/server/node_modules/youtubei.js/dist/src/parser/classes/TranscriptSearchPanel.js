import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import TranscriptFooter from './TranscriptFooter.js';
import TranscriptSearchBox from './TranscriptSearchBox.js';
import TranscriptSegmentList from './TranscriptSegmentList.js';
export default class TranscriptSearchPanel extends YTNode {
    static type = 'TranscriptSearchPanel';
    header;
    body;
    footer;
    target_id;
    constructor(data) {
        super();
        this.header = Parser.parseItem(data.header, TranscriptSearchBox);
        this.body = Parser.parseItem(data.body, TranscriptSegmentList);
        this.footer = Parser.parseItem(data.footer, TranscriptFooter);
        this.target_id = data.targetId;
    }
}
//# sourceMappingURL=TranscriptSearchPanel.js.map