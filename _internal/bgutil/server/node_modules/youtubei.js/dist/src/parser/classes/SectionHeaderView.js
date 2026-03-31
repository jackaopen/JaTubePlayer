import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class SectionHeaderView extends YTNode {
    static type = 'SectionHeaderView';
    headline;
    constructor(data) {
        super();
        this.headline = Text.fromAttributed(data.headline);
    }
}
//# sourceMappingURL=SectionHeaderView.js.map