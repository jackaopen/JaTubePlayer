import { YTNode } from '../../../helpers.js';
import Text from '../../misc/Text.js';
export default class LiveChatRestrictedParticipation extends YTNode {
    static type = 'LiveChatRestrictedParticipation';
    message;
    icon_type;
    constructor(data) {
        super();
        this.message = new Text(data.message);
        if (Reflect.has(data, 'icon') && Reflect.has(data.icon, 'iconType')) {
            this.icon_type = data.icon.iconType;
        }
        // TODO: parse onClickCommand
    }
}
//# sourceMappingURL=LiveChatRestrictedParticipation.js.map