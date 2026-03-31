import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ClipCreationTextInput extends YTNode {
    static type = 'ClipCreationTextInput';
    placeholder_text;
    max_character_limit;
    constructor(data) {
        super();
        this.placeholder_text = new Text(data.placeholderText);
        this.max_character_limit = data.maxCharacterLimit;
    }
}
//# sourceMappingURL=ClipCreationTextInput.js.map