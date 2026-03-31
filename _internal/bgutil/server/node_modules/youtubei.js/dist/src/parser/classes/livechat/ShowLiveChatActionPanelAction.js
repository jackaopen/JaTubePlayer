import { Parser } from '../../index.js';
import LiveChatActionPanel from './LiveChatActionPanel.js';
import { YTNode } from '../../helpers.js';
export default class ShowLiveChatActionPanelAction extends YTNode {
    static type = 'ShowLiveChatActionPanelAction';
    panel_to_show;
    constructor(data) {
        super();
        this.panel_to_show = Parser.parseItem(data.panelToShow, LiveChatActionPanel);
    }
}
//# sourceMappingURL=ShowLiveChatActionPanelAction.js.map