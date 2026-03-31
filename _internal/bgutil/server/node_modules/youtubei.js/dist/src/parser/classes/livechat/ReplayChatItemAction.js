import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class ReplayChatItemAction extends YTNode {
    static type = 'ReplayChatItemAction';
    actions;
    video_offset_time_msec;
    constructor(data) {
        super();
        this.actions = Parser.parseArray(data.actions?.map((action) => {
            delete action.clickTrackingParams;
            return action;
        }));
        this.video_offset_time_msec = data.videoOffsetTimeMsec;
    }
}
//# sourceMappingURL=ReplayChatItemAction.js.map