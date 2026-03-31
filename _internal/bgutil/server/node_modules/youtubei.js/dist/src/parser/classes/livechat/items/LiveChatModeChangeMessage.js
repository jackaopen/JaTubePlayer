import { YTNode } from '../../../helpers.js';
import Text from '../../misc/Text.js';
export default class LiveChatModeChangeMessage extends YTNode {
    static type = 'LiveChatModeChangeMessage';
    id;
    icon_type;
    text;
    subtext;
    timestamp;
    timestamp_usec;
    timestamp_text;
    constructor(data) {
        super();
        this.id = data.id;
        this.icon_type = data.icon.iconType;
        this.text = new Text(data.text);
        this.subtext = new Text(data.subtext);
        this.timestamp = Math.floor(parseInt(data.timestampUsec) / 1000);
        this.timestamp_usec = data.timestampUsec;
        this.timestamp_text = new Text(data.timestampText);
    }
}
//# sourceMappingURL=LiveChatModeChangeMessage.js.map