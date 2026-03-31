import { YTNode } from '../../helpers.js';
export default class UpdateSubscribeButtonAction extends YTNode {
    static type = 'UpdateSubscribeButtonAction';
    channel_id;
    subscribed;
    constructor(data) {
        super();
        this.channel_id = data.channelId;
        this.subscribed = data.subscribed;
    }
}
//# sourceMappingURL=UpdateSubscribeButtonAction.js.map