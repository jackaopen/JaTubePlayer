import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class ChannelAgeGate extends YTNode {
    static type = 'ChannelAgeGate';
    channel_title;
    avatar;
    header;
    main_text;
    sign_in_button;
    secondary_text;
    constructor(data) {
        super();
        this.channel_title = data.channelTitle;
        this.avatar = Thumbnail.fromResponse(data.avatar);
        this.header = new Text(data.header);
        this.main_text = new Text(data.mainText);
        this.sign_in_button = Parser.parseItem(data.signInButton, Button);
        this.secondary_text = new Text(data.secondaryText);
    }
}
//# sourceMappingURL=ChannelAgeGate.js.map