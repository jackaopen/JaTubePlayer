import Text from '../misc/Text.js';
import Thumbnail from '../misc/Thumbnail.js';
import CommentsSimplebox from './CommentsSimplebox.js';
import CommentsEntryPointTeaser from './CommentsEntryPointTeaser.js';
import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
export default class CommentsEntryPointHeader extends YTNode {
    static type = 'CommentsEntryPointHeader';
    header;
    comment_count;
    teaser_avatar;
    teaser_content;
    content_renderer;
    simplebox_placeholder;
    constructor(data) {
        super();
        if (Reflect.has(data, 'headerText')) {
            this.header = new Text(data.headerText);
        }
        if (Reflect.has(data, 'commentCount')) {
            this.comment_count = new Text(data.commentCount);
        }
        if (Reflect.has(data, 'teaserAvatar') || Reflect.has(data, 'simpleboxAvatar')) {
            this.teaser_avatar = Thumbnail.fromResponse(data.teaserAvatar || data.simpleboxAvatar);
        }
        if (Reflect.has(data, 'teaserContent')) {
            this.teaser_content = new Text(data.teaserContent);
        }
        if (Reflect.has(data, 'contentRenderer')) {
            this.content_renderer = Parser.parseItem(data.contentRenderer, [CommentsEntryPointTeaser, CommentsSimplebox]);
        }
        if (Reflect.has(data, 'simpleboxPlaceholder')) {
            this.simplebox_placeholder = new Text(data.simpleboxPlaceholder);
        }
    }
}
//# sourceMappingURL=CommentsEntryPointHeader.js.map