import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ButtonView from './ButtonView.js';
export default class ToggleButtonView extends YTNode {
    static type = 'ToggleButtonView';
    default_button;
    toggled_button;
    is_toggling_disabled;
    identifier;
    is_toggled;
    constructor(data) {
        super();
        this.default_button = Parser.parseItem(data.defaultButtonViewModel, ButtonView);
        this.toggled_button = Parser.parseItem(data.toggledButtonViewModel, ButtonView);
        this.is_toggling_disabled = data.isTogglingDisabled;
        this.identifier = data.identifier;
        if (Reflect.has(data, 'isToggled')) {
            this.is_toggled = data.isToggled;
        }
    }
}
//# sourceMappingURL=ToggleButtonView.js.map