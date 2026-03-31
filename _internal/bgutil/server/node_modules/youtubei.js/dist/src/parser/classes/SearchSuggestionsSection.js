import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class SearchSuggestionsSection extends YTNode {
    static type = 'SearchSuggestionsSection';
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents);
    }
}
//# sourceMappingURL=SearchSuggestionsSection.js.map