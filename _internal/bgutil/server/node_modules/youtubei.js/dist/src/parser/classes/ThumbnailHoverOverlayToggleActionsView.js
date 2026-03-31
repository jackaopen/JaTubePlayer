import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ToggleButtonView from './ToggleButtonView.js';
export default class ThumbnailHoverOverlayToggleActionsView extends YTNode {
    static type = 'ThumbnailHoverOverlayToggleActionsView';
    buttons;
    constructor(data) {
        super();
        this.buttons = Parser.parseArray(data.buttons, ToggleButtonView);
    }
}
//# sourceMappingURL=ThumbnailHoverOverlayToggleActionsView.js.map