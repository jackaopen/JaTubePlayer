import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import SearchFilterGroup from './SearchFilterGroup.js';
import Text from './misc/Text.js';
export default class SearchFilterOptionsDialog extends YTNode {
    static type = 'SearchFilterOptionsDialog';
    title;
    groups;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.groups = Parser.parseArray(data.groups, SearchFilterGroup);
    }
}
//# sourceMappingURL=SearchFilterOptionsDialog.js.map