import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class ChannelOwnerEmptyState extends YTNode {
    static type = 'ChannelOwnerEmptyState';
    illustration;
    description;
    constructor(data) {
        super();
        this.illustration = Thumbnail.fromResponse(data.illustration);
        this.description = new Text(data.description);
    }
}
//# sourceMappingURL=ChannelOwnerEmptyState.js.map