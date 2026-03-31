import { YTNode } from '../../helpers.js';
export default class HideEngagementPanelEndpoint extends YTNode {
    static type = 'HideEngagementPanelEndpoint';
    panel_identifier;
    constructor(data) {
        super();
        this.panel_identifier = data.panelIdentifier;
    }
}
//# sourceMappingURL=HideEngagementPanelEndpoint.js.map