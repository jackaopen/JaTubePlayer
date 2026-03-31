import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
export default class UpdateToggleButtonTextAction extends YTNode {
    static type = 'UpdateToggleButtonTextAction';
    default_text;
    toggled_text;
    button_id;
    constructor(data) {
        super();
        this.default_text = new Text(data.defaultText).toString();
        this.toggled_text = new Text(data.toggledText).toString();
        this.button_id = data.buttonId;
    }
}
//# sourceMappingURL=UpdateToggleButtonTextAction.js.map