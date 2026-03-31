import { YTNode } from '../../helpers.js';
export default class SignalAction extends YTNode {
    static type = 'SignalAction';
    signal;
    constructor(data) {
        super();
        this.signal = data.signal;
    }
}
//# sourceMappingURL=SignalAction.js.map