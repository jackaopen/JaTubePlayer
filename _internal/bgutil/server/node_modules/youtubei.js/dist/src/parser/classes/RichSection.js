import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class RichSection extends YTNode {
    static type = 'RichSection';
    content;
    full_bleed;
    target_id;
    constructor(data) {
        super();
        this.content = Parser.parseItem(data.content);
        this.full_bleed = !!data.fullBleed;
        if ('targetId' in data) {
            this.target_id = data.targetId;
        }
    }
}
//# sourceMappingURL=RichSection.js.map