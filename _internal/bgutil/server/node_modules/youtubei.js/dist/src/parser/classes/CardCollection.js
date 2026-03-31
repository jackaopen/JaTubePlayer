import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Text from './misc/Text.js';
export default class CardCollection extends YTNode {
    static type = 'CardCollection';
    cards;
    header;
    allow_teaser_dismiss;
    constructor(data) {
        super();
        this.cards = Parser.parseArray(data.cards);
        this.header = new Text(data.headerText);
        this.allow_teaser_dismiss = data.allowTeaserDismiss;
    }
}
//# sourceMappingURL=CardCollection.js.map