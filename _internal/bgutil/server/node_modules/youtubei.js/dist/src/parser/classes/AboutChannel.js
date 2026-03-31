import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import AboutChannelView from './AboutChannelView.js';
import Button from './Button.js';
export default class AboutChannel extends YTNode {
    static type = 'AboutChannel';
    metadata;
    share_channel;
    constructor(data) {
        super();
        this.metadata = Parser.parseItem(data.metadata, AboutChannelView);
        this.share_channel = Parser.parseItem(data.shareChannel, Button);
    }
}
//# sourceMappingURL=AboutChannel.js.map