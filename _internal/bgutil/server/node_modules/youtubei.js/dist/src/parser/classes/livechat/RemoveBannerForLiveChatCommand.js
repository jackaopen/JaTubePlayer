import { YTNode } from '../../helpers.js';
export default class RemoveBannerForLiveChatCommand extends YTNode {
    static type = 'RemoveBannerForLiveChatCommand';
    target_action_id;
    constructor(data) {
        super();
        this.target_action_id = data.targetActionId;
    }
}
//# sourceMappingURL=RemoveBannerForLiveChatCommand.js.map