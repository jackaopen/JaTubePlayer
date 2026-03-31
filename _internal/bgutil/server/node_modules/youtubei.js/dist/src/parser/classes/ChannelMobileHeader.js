import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class ChannelMobileHeader extends YTNode {
    static type = 'ChannelMobileHeader';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=ChannelMobileHeader.js.map