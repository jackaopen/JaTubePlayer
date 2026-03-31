import { YTNode } from '../../helpers.js';
export default class ShowEngagementPanelEndpoint extends YTNode {
    static type = 'ShowEngagementPanelEndpoint';
    panel_identifier;
    source_panel_identifier;
    constructor(data) {
        super();
        this.panel_identifier = data.panelIdentifier;
        this.source_panel_identifier = data.sourcePanelIdentifier;
    }
}
//# sourceMappingURL=ShowEngagementPanelEndpoint.js.map