import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class UpdateLiveChatPollAction extends YTNode {
    static type = 'UpdateLiveChatPollAction';
    poll_to_update;
    constructor(data) {
        super();
        this.poll_to_update = Parser.parseItem(data.pollToUpdate);
    }
}
//# sourceMappingURL=UpdateLiveChatPollAction.js.map