import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import Dropdown from './Dropdown.js';
import Text from './misc/Text.js';
export default class CreatePlaylistDialog extends YTNode {
    static type = 'CreatePlaylistDialog';
    title;
    title_placeholder;
    privacy_option;
    cancel_button;
    create_button;
    constructor(data) {
        super();
        this.title = new Text(data.dialogTitle).toString();
        this.title_placeholder = data.titlePlaceholder || '';
        this.privacy_option = Parser.parseItem(data.privacyOption, Dropdown);
        this.create_button = Parser.parseItem(data.cancelButton, Button);
        this.cancel_button = Parser.parseItem(data.cancelButton, Button);
    }
}
//# sourceMappingURL=CreatePlaylistDialog.js.map