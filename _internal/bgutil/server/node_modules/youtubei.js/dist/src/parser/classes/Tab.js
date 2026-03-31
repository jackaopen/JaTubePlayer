import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import SectionList from './SectionList.js';
import MusicQueue from './MusicQueue.js';
import RichGrid from './RichGrid.js';
import { YTNode } from '../helpers.js';
export default class Tab extends YTNode {
    static type = 'Tab';
    title;
    selected;
    endpoint;
    content;
    constructor(data) {
        super();
        this.title = data.title || 'N/A';
        this.selected = !!data.selected;
        this.endpoint = new NavigationEndpoint(data.endpoint);
        this.content = Parser.parseItem(data.content, [SectionList, MusicQueue, RichGrid]);
    }
}
//# sourceMappingURL=Tab.js.map