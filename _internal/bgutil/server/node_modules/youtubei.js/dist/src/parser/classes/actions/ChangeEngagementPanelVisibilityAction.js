import { YTNode } from '../../helpers.js';
export default class ChangeEngagementPanelVisibilityAction extends YTNode {
    static type = 'ChangeEngagementPanelVisibilityAction';
    target_id;
    visibility;
    constructor(data) {
        super();
        this.target_id = data.targetId;
        this.visibility = data.visibility;
    }
}
//# sourceMappingURL=ChangeEngagementPanelVisibilityAction.js.map