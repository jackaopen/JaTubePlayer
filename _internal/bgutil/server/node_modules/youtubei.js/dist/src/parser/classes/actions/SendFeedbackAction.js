import { YTNode } from '../../helpers.js';
export default class SendFeedbackAction extends YTNode {
    static type = 'SendFeedbackAction';
    bucket;
    constructor(data) {
        super();
        this.bucket = data.bucket;
    }
}
//# sourceMappingURL=SendFeedbackAction.js.map