import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
export default class SignalServiceEndpoint extends YTNode {
    static type = 'SignalServiceEndpoint';
    actions;
    signal;
    constructor(data) {
        super();
        if (Array.isArray(data.actions)) {
            this.actions = Parser.parseArray(data.actions.map((action) => {
                delete action.clickTrackingParams;
                return action;
            }));
        }
        this.signal = data.signal;
    }
}
//# sourceMappingURL=SignalServiceEndpoint.js.map