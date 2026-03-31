import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import ToggleButton from '../ToggleButton.js';
import Thumbnail from '../misc/Thumbnail.js';
import { InnertubeError } from '../../../utils/Utils.js';
export default class KidsBlocklistPickerItem extends YTNode {
    static type = 'KidsBlocklistPickerItem';
    #actions;
    child_display_name;
    child_account_description;
    avatar;
    block_button;
    blocked_entity_key;
    constructor(data) {
        super();
        this.child_display_name = new Text(data.childDisplayName);
        this.child_account_description = new Text(data.childAccountDescription);
        this.avatar = Thumbnail.fromResponse(data.avatar);
        this.block_button = Parser.parseItem(data.blockButton, [ToggleButton]);
        this.blocked_entity_key = data.blockedEntityKey;
    }
    async blockChannel() {
        if (!this.#actions)
            throw new InnertubeError('An active caller must be provide to perform this operation.');
        const button = this.block_button;
        if (!button)
            throw new InnertubeError('Block button was not found.', { child_display_name: this.child_display_name });
        if (button.is_toggled)
            throw new InnertubeError('This channel is already blocked.', { child_display_name: this.child_display_name });
        const response = await button.endpoint.call(this.#actions, { parse: false });
        return response;
    }
    setActions(actions) {
        this.#actions = actions;
    }
}
//# sourceMappingURL=KidsBlocklistPickerItem.js.map