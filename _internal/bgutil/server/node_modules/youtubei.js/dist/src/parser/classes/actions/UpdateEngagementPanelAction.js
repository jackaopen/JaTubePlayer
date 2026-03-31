import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import Transcript from '../Transcript.js';
export default class UpdateEngagementPanelAction extends YTNode {
    static type = 'UpdateEngagementPanelAction';
    target_id;
    content;
    constructor(data) {
        super();
        this.target_id = data.targetId;
        this.content = Parser.parseItem(data.content, Transcript);
    }
}
//# sourceMappingURL=UpdateEngagementPanelAction.js.map