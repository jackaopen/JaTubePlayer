import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
import Button from '../Button.js';
import { Parser } from '../../index.js';
import KidsBlocklistPickerItem from './KidsBlocklistPickerItem.js';
export default class KidsBlocklistPicker extends YTNode {
    static type = 'KidsBlocklistPicker';
    title;
    child_rows;
    done_button;
    successful_toast_action_message;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.child_rows = Parser.parse(data.childRows, true, [KidsBlocklistPickerItem]);
        this.done_button = Parser.parseItem(data.doneButton, [Button]);
        this.successful_toast_action_message = new Text(data.successfulToastActionMessage);
    }
}
//# sourceMappingURL=KidsBlocklistPicker.js.map