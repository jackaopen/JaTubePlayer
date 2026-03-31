import { YTNode } from '../../../helpers.js';
import { Parser } from '../../../index.js';
import BumperUserEduContentView from './BumperUserEduContentView.js';
export default class LiveChatItemBumperView extends YTNode {
    static type = 'LiveChatItemBumperView';
    content;
    constructor(data) {
        super();
        this.content = Parser.parseItem(data.content, BumperUserEduContentView);
    }
}
//# sourceMappingURL=LiveChatItemBumperView.js.map