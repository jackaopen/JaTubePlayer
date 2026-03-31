import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import SecondarySearchContainer from './SecondarySearchContainer.js';
import RichGrid from './RichGrid.js';
import SectionList from './SectionList.js';
export default class TwoColumnSearchResults extends YTNode {
    static type = 'TwoColumnSearchResults';
    header;
    primary_contents;
    secondary_contents;
    target_id;
    constructor(data) {
        super();
        this.header = Parser.parseItem(data.header);
        this.primary_contents = Parser.parseItem(data.primaryContents, [RichGrid, SectionList]);
        this.secondary_contents = Parser.parseItem(data.secondaryContents, [SecondarySearchContainer]);
        if ('targetId' in data) {
            this.target_id = data.targetId;
        }
    }
}
//# sourceMappingURL=TwoColumnSearchResults.js.map