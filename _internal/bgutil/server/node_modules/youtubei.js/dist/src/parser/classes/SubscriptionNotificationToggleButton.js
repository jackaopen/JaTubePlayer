import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class SubscriptionNotificationToggleButton extends YTNode {
    static type = 'SubscriptionNotificationToggleButton';
    states;
    current_state_id;
    target_id;
    constructor(data) {
        super();
        this.states = data.states.map((data) => ({
            id: data.stateId,
            next_id: data.nextStateId,
            state: Parser.parse(data.state)
        }));
        this.current_state_id = data.currentStateId;
        this.target_id = data.targetId;
    }
}
//# sourceMappingURL=SubscriptionNotificationToggleButton.js.map