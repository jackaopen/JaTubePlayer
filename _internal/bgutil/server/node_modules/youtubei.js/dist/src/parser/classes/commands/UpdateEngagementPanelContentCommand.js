import { YTNode } from '../../helpers.js';
export default class UpdateEngagementPanelContentCommand extends YTNode {
    static type = 'UpdateEngagementPanelContentCommand';
    content_source_panel_identifier;
    target_panel_identifier;
    constructor(data) {
        super();
        this.content_source_panel_identifier = data.contentSourcePanelIdentifier;
        this.target_panel_identifier = data.targetPanelIdentifier;
    }
}
//# sourceMappingURL=UpdateEngagementPanelContentCommand.js.map