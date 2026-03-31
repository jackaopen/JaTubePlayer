import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class MusicResponsiveListItemFlexColumn extends YTNode {
    static type = 'MusicResponsiveListItemFlexColumn';
    title;
    display_priority;
    constructor(data) {
        super();
        this.title = new Text(data.text);
        this.display_priority = data.displayPriority;
    }
}
//# sourceMappingURL=MusicResponsiveListItemFlexColumn.js.map