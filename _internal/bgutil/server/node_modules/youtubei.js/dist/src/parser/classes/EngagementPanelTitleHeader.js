import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Text from './misc/Text.js';
import Button from './Button.js';
export default class EngagementPanelTitleHeader extends YTNode {
    static type = 'EngagementPanelTitleHeader';
    title;
    visibility_button;
    contextual_info;
    menu;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.contextual_info = data.contextualInfo ? new Text(data.contextualInfo) : undefined;
        this.visibility_button = Parser.parseItem(data.visibilityButton, Button);
        this.menu = Parser.parseItem(data.menu);
    }
}
//# sourceMappingURL=EngagementPanelTitleHeader.js.map