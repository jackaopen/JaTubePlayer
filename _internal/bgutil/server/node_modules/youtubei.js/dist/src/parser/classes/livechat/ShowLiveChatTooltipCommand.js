import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class ShowLiveChatTooltipCommand extends YTNode {
    static type = 'ShowLiveChatTooltipCommand';
    tooltip;
    constructor(data) {
        super();
        this.tooltip = Parser.parseItem(data.tooltip);
    }
}
//# sourceMappingURL=ShowLiveChatTooltipCommand.js.map