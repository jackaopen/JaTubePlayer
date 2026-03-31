import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class SettingsCheckbox extends YTNode {
    static type = 'SettingsCheckbox';
    title;
    help_text;
    enabled;
    disabled;
    id;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.help_text = new Text(data.helpText);
        this.enabled = data.enabled;
        this.disabled = data.disabled;
        this.id = data.id;
    }
}
//# sourceMappingURL=SettingsCheckbox.js.map