import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ToggleButtonView from './ToggleButtonView.js';
export default class DislikeButtonView extends YTNode {
    static type = 'DislikeButtonView';
    toggle_button;
    dislike_entity_key;
    constructor(data) {
        super();
        this.toggle_button = Parser.parseItem(data.toggleButtonViewModel, ToggleButtonView);
        this.dislike_entity_key = data.dislikeEntityKey;
    }
}
//# sourceMappingURL=DislikeButtonView.js.map