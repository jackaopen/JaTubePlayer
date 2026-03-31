import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class MusicResponsiveListItemFixedColumn extends YTNode {
    static type = 'musicResponsiveListItemFlexColumnRenderer';
    title;
    display_priority;
    constructor(data) {
        super();
        this.title = new Text(data.text);
        this.display_priority = data.displayPriority;
    }
}
//# sourceMappingURL=MusicResponsiveListItemFixedColumn.js.map