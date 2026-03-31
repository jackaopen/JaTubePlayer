import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
export default class TopbarMenuButton extends YTNode {
    static type = 'TopbarMenuButton';
    icon_type;
    menu_renderer;
    target_id;
    constructor(data) {
        super();
        if (Reflect.has(data, 'icon') && Reflect.has(data.icon, 'iconType'))
            this.icon_type = data.icon.iconType;
        this.menu_renderer = Parser.parseItem(data.menuRenderer);
        this.target_id = data.targetId;
    }
}
//# sourceMappingURL=TopbarMenuButton.js.map