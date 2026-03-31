import Text from '../misc/Text.js';
import Thumbnail from '../misc/Thumbnail.js';
import { YTNode } from '../../helpers.js';
export default class CommentsEntryPointTeaser extends YTNode {
    static type = 'CommentsEntryPointTeaser';
    teaser_avatar;
    teaser_content;
    constructor(data) {
        super();
        if (Reflect.has(data, 'teaserAvatar')) {
            this.teaser_avatar = Thumbnail.fromResponse(data.teaserAvatar);
        }
        if (Reflect.has(data, 'teaserContent')) {
            this.teaser_content = new Text(data.teaserContent);
        }
    }
}
//# sourceMappingURL=CommentsEntryPointTeaser.js.map