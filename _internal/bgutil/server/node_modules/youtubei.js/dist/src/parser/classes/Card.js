import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class Card extends YTNode {
    static type = 'Card';
    teaser;
    content;
    card_id;
    feature;
    cue_ranges;
    constructor(data) {
        super();
        this.teaser = Parser.parseItem(data.teaser);
        this.content = Parser.parseItem(data.content);
        if (Reflect.has(data, 'cardId')) {
            this.card_id = data.cardId;
        }
        if (Reflect.has(data, 'feature')) {
            this.feature = data.feature;
        }
        this.cue_ranges = data.cueRanges.map((cr) => ({
            start_card_active_ms: cr.startCardActiveMs,
            end_card_active_ms: cr.endCardActiveMs,
            teaser_duration_ms: cr.teaserDurationMs,
            icon_after_teaser_ms: cr.iconAfterTeaserMs
        }));
    }
}
//# sourceMappingURL=Card.js.map