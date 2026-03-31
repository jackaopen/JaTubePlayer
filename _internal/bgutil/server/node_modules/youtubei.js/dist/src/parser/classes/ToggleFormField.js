import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ToggleFormField extends YTNode {
    static type = 'ToggleFormField';
    label;
    toggled;
    toggle_on_action;
    toggle_off_action;
    constructor(data) {
        super();
        this.label = new Text(data.label);
        this.toggled = data.toggled;
        if ('toggleOnAction' in data)
            this.toggle_on_action = new NavigationEndpoint(data.toggleOnAction);
        if ('toggleOffAction' in data)
            this.toggle_off_action = new NavigationEndpoint(data.toggleOffAction);
    }
}
//# sourceMappingURL=ToggleFormField.js.map