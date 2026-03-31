import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class ChannelExternalLinkView extends YTNode {
    static type = 'ChannelExternalLinkView';
    title;
    link;
    favicon;
    constructor(data) {
        super();
        this.title = Text.fromAttributed(data.title);
        this.link = Text.fromAttributed(data.link);
        this.favicon = Thumbnail.fromResponse(data.favicon);
    }
}
//# sourceMappingURL=ChannelExternalLinkView.js.map